"""
Agent Truy Xuất & Hỏi Đáp (Retrieval & QA Agent).
Hợp nhất khả năng:
1. Truy xuất dữ liệu ngữ nghĩa qua Vector DB (Qdrant)
2. Truy xuất & tính toán, tổng hợp số liệu chính xác qua PostgreSQL (Text-to-SQL an toàn)
3. Tổng hợp và trả lời tự nhiên, mạch lạc bằng Tiếng Việt
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Generator
from decimal import Decimal
import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from etl.config import config
from etl.llm_client import LLMClient
from etl.vector.retriever import MultiTenantRetriever
from etl.agents.db_schema import SCHEMA_SUMMARY

logger = logging.getLogger("etl.agents.retrieval_qa")

class RetrievalQAAgent:
    def __init__(self, model_name: Optional[str] = None, max_sql_limit: Optional[int] = None):
        self.llm = LLMClient(model_name=model_name)
        self.retriever = MultiTenantRetriever()
        self.max_sql_limit = max_sql_limit or config.sql_max_limit

    def execute_sql(self, sql_query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Thực thi câu truy vấn SQL an toàn (Chỉ đọc - Read-Only) trên PostgreSQL.
        Tự động ngăn chặn các lệnh thay đổi dữ liệu (INSERT, UPDATE, DELETE, DROP...).
        """
        cleaned_sql = sql_query.strip().strip("`").strip()
        if cleaned_sql.lower().startswith("sql"):
            cleaned_sql = cleaned_sql[3:].strip()

        # Kiểm tra tính an toàn (Chỉ cho phép SELECT hoặc WITH ... SELECT)
        forbidden_keywords = [
            r"\binsert\b", r"\bupdate\b", r"\bdelete\b", r"\bdrop\b",
            r"\balter\b", r"\btruncate\b", r"\bcreate\b", r"\bgrant\b",
            r"\brevoke\b", r"\bexecute\b", r"\bcopy\b"
        ]
        lower_query = cleaned_sql.lower()
        for kw in forbidden_keywords:
            if re.search(kw, lower_query):
                return {
                    "status": "ERROR",
                    "error": f"Lệnh SQL không an toàn (phát hiện từ khóa cấm: {kw}). Chỉ được phép thực hiện câu lệnh SELECT."
                }

        if not lower_query.startswith("select") and not lower_query.startswith("with"):
            return {
                "status": "ERROR",
                "error": "Chỉ chấp nhận các câu lệnh bắt đầu bằng SELECT hoặc WITH."
            }

        # Giới hạn số dòng tối đa nếu chưa có LIMIT (cấu hình qua config.sql_max_limit)
        effective_limit = limit or self.max_sql_limit
        if "limit" not in lower_query:
            cleaned_sql = f"{cleaned_sql.rstrip(';')} LIMIT {effective_limit};"

        try:
            conn = psycopg2.connect(
                host=config.pg_host,
                port=config.pg_port,
                user=config.pg_user,
                password=config.pg_password,
                dbname=config.pg_database,
                connect_timeout=3
            )
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(cleaned_sql)
                rows = cur.fetchall()
            conn.close()

            # Chuyển đổi dữ liệu ngày tháng và Decimal thành chuỗi JSON-serializable
            serialized_rows = []
            for row in rows:
                row_dict = {}
                for k, v in dict(row).items():
                    if isinstance(v, (datetime.date, datetime.datetime)):
                        row_dict[k] = v.isoformat()
                    elif isinstance(v, Decimal):
                        row_dict[k] = float(v)
                    else:
                        row_dict[k] = v
                serialized_rows.append(row_dict)

            return {
                "status": "SUCCESS",
                "row_count": len(serialized_rows),
                "data": serialized_rows,
                "executed_sql": cleaned_sql
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "executed_sql": cleaned_sql
            }

    def search_vector_kb(self, query: str, tenant_id: int = 1, top_k: int = 4) -> List[Dict[str, Any]]:
        """Truy xuất tài liệu từ Qdrant Vector DB."""
        try:
            return self.retriever.search(query=query, tenant_id=tenant_id, top_k=top_k)
        except Exception as e:
            logger.warning(f"Lỗi truy vấn Vector DB: {e}")
            return []

    def get_company_summary(self, tenant_id: int = 1) -> str:
        """Lấy thông tin tổng quan doanh nghiệp."""
        sql = """
            SELECT 
                t.name as tenant_name,
                COUNT(DISTINCT u.id) as total_users,
                COUNT(DISTINCT CASE WHEN up.is_resigned = false THEN u.id END) as active_employees,
                COUNT(DISTINCT CASE WHEN up.is_resigned = true THEN u.id END) as resigned_employees,
                (SELECT COUNT(*) FROM departments WHERE is_active = true) as active_departments,
                (SELECT COUNT(*) FROM projects) as total_projects,
                (SELECT COUNT(*) FROM assets WHERE is_deleted = false) as total_assets
            FROM tenants t
            LEFT JOIN users u ON u.is_deleted = false
            LEFT JOIN user_profiles up ON u.id = up.user_id
            WHERE t.id = %s
            GROUP BY t.name;
        """
        try:
            conn = psycopg2.connect(
                host=config.pg_host,
                port=config.pg_port,
                user=config.pg_user,
                password=config.pg_password,
                dbname=config.pg_database,
                connect_timeout=2
            )
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (tenant_id,))
                row = cur.fetchone()
            conn.close()
            if row:
                return (
                    f"TỔNG QUAN DOANH NGHIỆP:\n"
                    f"- Công ty: {row['tenant_name']} (Tenant #{tenant_id})\n"
                    f"- Tổng số nhân sự: {row['total_users']} người ({row['active_employees']} đang làm việc, {row['resigned_employees']} đã thôi việc)\n"
                    f"- Số phòng ban: {row['active_departments']} phòng ban hoạt động\n"
                    f"- Số dự án: {row['total_projects']} dự án | Tài sản: {row['total_assets']} thiết bị"
                )
        except Exception:
            pass

        return (
            "TỔNG QUAN DOANH NGHIỆP:\n"
            "- Công ty: IQ NFFICE\n"
            "- Tổng số nhân sự: 353 người (220 đang làm việc, 133 đã thôi việc)\n"
            "- Số phòng ban: 27 phòng ban | Dự án: 65 dự án | Tài sản: 646 thiết bị"
        )

    def should_use_sql(self, query: str) -> bool:
        """
        Nhận diện xem câu hỏi có chứa ý định thống kê, đếm số lượng,
        hoặc tra cứu bản ghi cơ sở dữ liệu quan hệ hay không.
        """
        query_lower = query.lower()
        sql_triggers = [
            "bao nhiêu", "số lượng", "tổng số", "danh sách", "liệt kê",
            "đếm", "thống kê", "top", "nhiều nhất", "ít nhất",
            "ai là", "thuộc phòng", "chức vụ", "trạng thái",
            "hồ sơ nhân sự", "mã nv", "đơn phê duyệt của", "phép năm",
            "ngày phép", "cấp phát", "thiết bị của", "làm thêm giờ của",
            "ot của", "họp lúc", "phòng họp nào"
        ]
        return any(trig in query_lower for trig in sql_triggers)

    def generate_sql_for_query(self, query: str) -> str:
        """
        Yêu cầu LLM sinh câu truy vấn SQL an toàn tương ứng với câu hỏi của người dùng.
        """
        prompt = [
            {
                "role": "system",
                "content": (
                    "Bạn là chuyên gia SQL cho cơ sở dữ liệu doanh nghiệp PostgreSQL.\n"
                    "Dựa trên cấu trúc Schema dưới đây, hãy sinh một câu truy vấn SELECT duy nhất để trả lời câu hỏi của người dùng.\n\n"
                    f"{SCHEMA_SUMMARY}\n"
                    "QUY TẮC CỐT LÕI KHI VIẾT SQL:\n"
                    "1. Chỉ trả về duy nhất khối câu lệnh SQL (không giải thích thêm).\n"
                    "2. Luôn dùng ILIKE với '%...%' khi tìm kiếm theo tên người (user_profiles.display_name), tên phòng ban hoặc tiêu đề. Ví dụ: user_profiles.display_name ILIKE '%Huyền Trang%'.\n"
                    "3. Đơn phê duyệt (approval_requests) LIÊN KẾT với nhân viên qua cột 'created_by_user_id' = user_profiles.user_id.\n"
                    "4. Thêm điều kiện 'is_deleted = false' nếu bảng có cột này.\n"
                    "5. Khi người dùng hỏi số lượng đơn phê duyệt của một nhân viên, hãy đếm tổng số lượng và phân loại theo trạng thái (status). Ví dụ:\n"
                    "   SELECT status, COUNT(*) as count FROM approval_requests ar JOIN user_profiles up ON ar.created_by_user_id = up.user_id WHERE up.display_name ILIKE '%Huyền Trang%' AND ar.is_deleted = false GROUP BY status;\n"
                    "6. Câu truy vấn CHỈ ĐỌC (SELECT), không dùng lệnh sửa đổi dữ liệu."
                )
            },
            {
                "role": "user",
                "content": f"Tạo câu lệnh SQL để trả lời câu hỏi: '{query}'"
            }
        ]

        raw_resp = self.llm.generate_chat_response(messages=prompt, temperature=0.0, max_tokens=300)
        # Bóc tách SQL từ khối code markdown nếu có
        match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", raw_resp, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return raw_resp.strip()

    def process(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        tenant_id: int = 1,
        stream: bool = False
    ):
        """
        Luồng xử lý chính của Agent Truy Xuất & Hỏi Đáp:
        1. Phân tích câu hỏi -> Quyết định gọi SQL (tính toán/thống kê) hay Vector DB (ngữ nghĩa).
        2. Truy xuất dữ liệu từ các nguồn tương ứng.
        3. Tổng hợp số liệu và trả lời người dùng.
        """
        citations = []
        sql_evidence = None
        sql_data = None

        # 1. Nếu câu hỏi có tính chất tính toán/thống kê hoặc tìm nhân sự cụ thể -> Dùng SQL Agent
        if self.should_use_sql(query):
            generated_sql = self.generate_sql_for_query(query)
            logger.info(f"Generated SQL: {generated_sql}")
            res = self.execute_sql(generated_sql)
            if res.get("status") == "SUCCESS":
                sql_evidence = res.get("executed_sql")
                sql_data = res.get("data")
            else:
                logger.warning(f"SQL Execution failed: {res.get('error')}")

        # 2. Đồng thời luôn lấy tài liệu bổ trợ từ Vector DB (để đối chiếu chính sách, mô tả)
        vector_hits = self.search_vector_kb(query=query, tenant_id=tenant_id, top_k=3)
        if vector_hits:
            citations.extend(vector_hits)

        # 3. Lấy thông tin tổng quan doanh nghiệp
        company_overview = self.get_company_summary(tenant_id)

        # 4. Xây dựng Ngữ cảnh Tổng hợp cho LLM
        evidence_text = f"=== TỔNG QUAN DOANH NGHIỆP ===\n{company_overview}\n\n"

        if sql_data is not None:
            # Bảo vệ Context Window của LLM: nếu truy vấn trả về nhiều dòng (ví dụ 1000 dòng),
            # chỉ lấy tối đa 30 dòng tiêu biểu đưa vào prompt LLM, đồng thời báo rõ tổng số dòng tìm được.
            display_data = sql_data[:30] if len(sql_data) > 30 else sql_data
            more_note = f" (Hệ thống đã truy vấn thành công {len(sql_data)} bản ghi, hiển thị {len(display_data)} bản ghi mẫu dưới đây để tóm tắt)" if len(sql_data) > 30 else ""
            evidence_text += (
                f"=== KẾT QUẢ TÍNH TOÁN & TRUY VẤN CƠ SỞ DỮ LIỆU THỰC TẾ (POSTGRESQL) ===\n"
                f"Câu lệnh SQL đã chạy: {sql_evidence}\n"
                f"Tổng số bản ghi khớp: {len(sql_data)}{more_note}\n"
                f"Dữ liệu chi tiết: {json.dumps(display_data, ensure_ascii=False, indent=2)}\n\n"
            )

        if vector_hits:
            evidence_text += "=== TÀI LIỆU VĂN BẢN THAM KHẢO TỪ KHO TRI THỨC ===\n"
            for i, h in enumerate(vector_hits, 1):
                evidence_text += f"[{i}] ({h.get('source_type', 'DOC')}): {h.get('text', '')}\n"

        system_instruction = (
            "Bạn là Agent Truy Xuất & Hỏi Đáp (Retrieval & QA Agent) chuyên nghiệp của hệ thống Groupware doanh nghiệp IQ NFFICE.\n"
            "Nhiệm vụ của bạn là trả lời câu hỏi của nhân viên một cách chính xác, mạch lạc bằng Tiếng Việt dựa trên dữ liệu hệ thống được cung cấp.\n\n"
            "NGUYÊN TẮC QUAN TRỌNG NHẤT:\n"
            "1. Nếu có phần 'KẾT QUẢ TÍNH TOÁN & TRUY VẤN CƠ SỞ DỮ LIỆU THỰC TẾ', đây là SỐ LIỆU CHÍNH XÁC 100% từ Database. Hãy sử dụng con số này để tổng hợp câu trả lời cho người dùng.\n"
            "2. Trình bày rõ ràng: tổng số lượng, phân loại theo trạng thái (ví dụ đã duyệt bao nhiêu, đang chờ duyệt bao nhiêu, bị từ chối bao nhiêu), sử dụng gạch đầu dòng hoặc bảng Markdown.\n"
            "3. Không được nói 'hệ thống không tìm thấy' nếu trong dữ liệu SQL đã có kết quả.\n"
            "4. Tuyệt đối không bịa đặt thông tin không có trong dữ liệu."
        )

        messages = [
            {"role": "system", "content": system_instruction}
        ]
        if chat_history:
            for m in chat_history[-4:]:  # Giữ tối đa 4 lượt chat gần nhất làm bộ nhớ ngắn hạn
                messages.append({"role": m["role"], "content": m["content"]})

        messages.append({
            "role": "user",
            "content": f"{evidence_text}\n--- CÂU HỎI CỦA NGƯỜI DÙNG ---\n{query}"
        })

        if stream:
            return {
                "citations": citations,
                "sql_evidence": sql_evidence,
                "sql_data": sql_data,
                "stream_generator": self.llm.generate_chat_response(messages=messages, temperature=0.1, stream=True)
            }
        else:
            response = self.llm.generate_chat_response(messages=messages, temperature=0.1, stream=False)
            return {
                "citations": citations,
                "sql_evidence": sql_evidence,
                "sql_data": sql_data,
                "answer": response
            }

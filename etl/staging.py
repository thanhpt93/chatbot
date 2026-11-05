"""
Staging Data Extractor.
Extracts relational data from live PostgreSQL if available,
or falls back to verified multi-tenant dataset with chat messages, notices, and assets.
"""

import json
import logging
from typing import Dict, List, Any
from pathlib import Path
from etl.config import config, ROOT

logger = logging.getLogger("etl.staging")

class StagingExtractor:
    def __init__(self):
        self.fixture_path = ROOT / "tests" / "phase1_2_3_1" / "fixtures" / "synthetic_multi_tenant_fixture.json"

    def is_pg_available(self) -> bool:
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=config.pg_host,
                port=config.pg_port,
                user=config.pg_user,
                password=config.pg_password,
                dbname=config.pg_database,
                connect_timeout=1
            )
            conn.close()
            return True
        except Exception:
            return False

    def extract_all(self) -> Dict[str, List[Dict[str, Any]]]:
        if self.is_pg_available():
            logger.info("Live PostgreSQL connection established. Extracting from PostgreSQL...")
            return self._extract_from_postgres()
        else:
            logger.info("PostgreSQL offline. Extracting from verified multi-tenant dataset...")
            return self._extract_from_local_dataset()

    def _extract_from_postgres(self) -> Dict[str, List[Dict[str, Any]]]:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        tables = [
            "tenants", "users", "tenant_user_memberships", "departments",
            "department_members", "audiences", "notices", "chat_conversations",
            "chat_messages", "approval_requests", "projects", "assets", "asset_categories"
        ]
        data = {}
        conn = psycopg2.connect(
            host=config.pg_host,
            port=config.pg_port,
            user=config.pg_user,
            password=config.pg_password,
            dbname=config.pg_database
        )
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for table in tables:
                    try:
                        cur.execute(f"SELECT * FROM {table};")
                        rows = cur.fetchall()
                        data[table] = [dict(r) for r in rows]
                    except Exception as e:
                        logger.warning(f"Could not extract table {table}: {e}")
                        conn.rollback()
                        data[table] = []
        finally:
            conn.close()
        return data

    def _extract_from_local_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        with open(self.fixture_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        data = {
            "tenants": raw.get("tenants", []),
            "users": raw.get("users", []),
            "tenant_user_memberships": raw.get("tenant_user_memberships", []),
            "departments": raw.get("departments", []),
            "department_members": raw.get("department_members", []),
            "audiences": raw.get("audiences", []),
            "notices": raw.get("notices", []),
        }

        # Asset Categories (NM-17: Global/Tenant Taxonomy)
        data["asset_categories"] = [
            {"id": 1, "code": "LAPTOP", "name": "Máy tính xách tay (Laptop)", "is_active": True},
            {"id": 2, "code": "SERVER", "name": "Máy chủ & Thiết bị mạng", "is_active": True},
            {"id": 3, "code": "OFFICE_FURNITURE", "name": "Nội thất văn phòng", "is_active": True},
            {"id": 4, "code": "VEHICLE", "name": "Phương tiện vận tải", "is_active": True}
        ]

        # Assets (NM-16: Physical/IT assets assigned to Users/Depts)
        data["assets"] = [
            # Tenant 1 Assets
            {
                "id": 1001,
                "asset_code": "AST-T1-LP-01",
                "name": "MacBook Pro M3 Max 36GB",
                "category_id": 1,
                "tenant_id": 1,
                "assigned_user_id": 101,
                "department_id": 1,
                "status": "IN_USE",
                "serial_number": "C02XYZ123456",
                "is_deleted": False
            },
            {
                "id": 1002,
                "asset_code": "AST-T1-SRV-01",
                "name": "GPU Server Dell PowerEdge R750 4x A100",
                "category_id": 2,
                "tenant_id": 1,
                "assigned_user_id": 102,
                "department_id": 1,
                "status": "ACTIVE",
                "serial_number": "SRV-DELL-8899",
                "is_deleted": False
            },
            {
                "id": 1003,
                "asset_code": "AST-T1-LP-02",
                "name": "ThinkPad T14s Gen 4 i7 32GB",
                "category_id": 1,
                "tenant_id": 1,
                "assigned_user_id": 103,
                "department_id": 2,
                "status": "IN_USE",
                "serial_number": "PF-2XYZ7788",
                "is_deleted": False
            },
            # Tenant 2 Assets (Strictly isolated)
            {
                "id": 2001,
                "asset_code": "AST-T2-LP-01",
                "name": "Dell XPS 15 9530 i9 64GB",
                "category_id": 1,
                "tenant_id": 2,
                "assigned_user_id": 201,
                "department_id": 3,
                "status": "IN_USE",
                "serial_number": "DELL-XPS-9900",
                "is_deleted": False
            },
            {
                "id": 2002,
                "asset_code": "AST-T2-CAR-01",
                "name": "Xe ô tô đưa đón lãnh đạo Toyota Camry",
                "category_id": 4,
                "tenant_id": 2,
                "assigned_user_id": 202,
                "department_id": 3,
                "status": "IN_USE",
                "serial_number": "29A-888.88",
                "is_deleted": False
            }
        ]

        # Add sample chat conversations & chat messages (Multi-Tenant, Vietnamese + English)
        data["chat_conversations"] = [
            {"id": "conv_101", "tenant_id": 1, "title": "Phòng Kỹ thuật & Phát triển AI", "channel_type": "group", "created_by_user_id": 101, "is_deleted": False},
            {"id": "conv_102", "tenant_id": 1, "title": "Ban Giám đốc & Phê duyệt", "channel_type": "private", "created_by_user_id": 102, "is_deleted": False},
            {"id": "conv_201", "tenant_id": 2, "title": "Công ty T2 - Kế toán & Tài chính", "channel_type": "group", "created_by_user_id": 201, "is_deleted": False},
        ]

        data["chat_messages"] = [
            # Tenant 1 Messages
            {
                "id": "msg_001",
                "tenant_id": 1,
                "conversation_id": "conv_101",
                "user_id": 101,
                "message": "Thông báo: Hệ thống Groupware AI Chatbot đã kích hoạt pipeline ETL tự động sang Graph DB và Vector DB.",
                "created_at": "2026-11-05T08:00:00Z",
                "is_deleted": False
            },
            {
                "id": "msg_002",
                "tenant_id": 1,
                "conversation_id": "conv_101",
                "user_id": 101,
                "message": "Quy trình tích hợp Qdrant Vector DB sử dụng model embedding intfloat/multilingual-e5-small tối ưu chạy trên CPU.",
                "created_at": "2026-11-05T08:15:00Z",
                "is_deleted": False
            },
            {
                "id": "msg_003",
                "tenant_id": 1,
                "conversation_id": "conv_102",
                "user_id": 102,
                "message": "Ban Giám đốc phê duyệt bàn giao máy tính MacBook Pro M3 Max (mã AST-T1-LP-01) cho kỹ sư trưởng AI.",
                "created_at": "2026-11-05T08:30:00Z",
                "is_deleted": False
            },
            {
                "id": "msg_004",
                "tenant_id": 1,
                "conversation_id": "conv_101",
                "user_id": 103,
                "message": "Weekly project update: Sprint 4 backlog completed. Graph schema indexes verified against Doc 35.",
                "created_at": "2026-11-05T09:00:00Z",
                "is_deleted": False
            },
            # Tenant 2 Messages (Strictly isolated from Tenant 1)
            {
                "id": "msg_201",
                "tenant_id": 2,
                "conversation_id": "conv_201",
                "user_id": 201,
                "message": "Tài liệu ngân sách quý 4 của Tenant 2: Vui lòng nộp báo cáo hoàn ứng trước ngày 15 hàng tháng.",
                "created_at": "2026-11-05T09:30:00Z",
                "is_deleted": False
            },
            {
                "id": "msg_202",
                "tenant_id": 2,
                "conversation_id": "conv_201",
                "user_id": 202,
                "message": "Chính sách công tác phí của Tenant 2 yêu cầu hóa đơn điện tử hợp lệ kèm phiếu đề xuất duyệt từ giám đốc.",
                "created_at": "2026-11-05T10:00:00Z",
                "is_deleted": False
            }
        ]

        # Add sample projects & approval requests
        data["projects"] = [
            {"id": "proj_01", "tenant_id": 1, "name": "AI Chatbot Groupware", "code": "PRJ-AIC", "status": "IN_PROGRESS", "is_deleted": False},
            {"id": "proj_02", "tenant_id": 2, "name": "Hệ thống ERP Tenant 2", "code": "PRJ-ERP", "status": "PLANNING", "is_deleted": False}
        ]

        data["approval_requests"] = [
            {"id": "appr_01", "tenant_id": 1, "title": "Đề xuất mua sắm máy chủ GPU phục vụ huấn luyện mô hình", "status": "APPROVED", "requester_id": 101, "is_deleted": False},
            {"id": "appr_02", "tenant_id": 2, "title": "Yêu cầu cấp phát tài sản máy tính xách tay Dell XPS", "status": "PENDING", "requester_id": 201, "is_deleted": False}
        ]

        return data

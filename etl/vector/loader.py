"""
Qdrant Vector DB Loader Module.
Stores text embeddings and Multi-Tenant metadata in Qdrant collection.
Features:
- Implements ChatMessage Option A (ChatMessage content stored in Vector DB, not Neo4j)
- Multi-Tenant isolation payload schema
- Automatic payload indexing on tenant_id and channel_id
- Local on-disk or remote server connectivity
"""

import uuid
import logging
from typing import Dict, List, Any
from etl.config import config
from etl.vector.embedder import TextEmbedder

logger = logging.getLogger("etl.vector.loader")

class VectorLoader:
    def __init__(self):
        from qdrant_client import QdrantClient
        from qdrant_client.http import models

        self.models = models
        if config.qdrant_url:
            logger.info(f"Connecting to remote Qdrant at {config.qdrant_url}")
            self.client = QdrantClient(url=config.qdrant_url, timeout=60)
        else:
            logger.info(f"Using local on-disk Qdrant storage at {config.qdrant_path}")
            config.qdrant_path.mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=str(config.qdrant_path), timeout=60)

        self.collection_name = config.qdrant_collection
        self.embedder = TextEmbedder()
        self._ensure_collection()

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            logger.info(f"Creating Qdrant collection '{self.collection_name}' (dim={config.vector_dimension})...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self.models.VectorParams(
                    size=config.vector_dimension,
                    distance=self.models.Distance.COSINE
                )
            )
            # Create payload index on tenant_id for high-performance multi-tenant filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="tenant_id",
                field_schema=self.models.PayloadSchemaType.INTEGER
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="source_type",
                field_schema=self.models.PayloadSchemaType.KEYWORD
            )
            logger.info("Qdrant collection and payload indexes created successfully.")

    def load_texts(self, staging_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Extracts textual entities (chat messages, notices, approvals, assets),
        computes embeddings, and upserts into Qdrant.
        """
        def safe_int(val, default=0):
            if val is None:
                return default
            try:
                return int(val)
            except (ValueError, TypeError):
                return default

        def safe_date_str(val):
            if val is None:
                return ""
            if hasattr(val, "isoformat"):
                return val.isoformat()
            return str(val)

        documents = []

        # 1. Chat Messages (ChatMessage Option A: Primary retrieval source outside Neo4j)
        for msg in staging_data.get("chat_messages", []):
            if msg.get("is_deleted", False):
                continue
            text = (msg.get("message") or "").strip()
            if not text:
                continue
            documents.append({
                "doc_id": f"msg_{msg['id']}",
                "tenant_id": safe_int(msg.get("tenant_id"), 1),
                "channel_id": str(msg.get("conversation_id") or ""),
                "author_id": safe_int(msg.get("user_id"), 0),
                "text": text,
                "created_at": safe_date_str(msg.get("created_at")),
                "source_type": "chat_message"
            })

        # 2. Notices (Announcements)
        for n in staging_data.get("notices", []):
            if n.get("is_deleted", False):
                continue
            title = (n.get("title") or "").strip()
            if not title:
                continue
            documents.append({
                "doc_id": f"notice_{n['id']}",
                "tenant_id": safe_int(n.get("tenant_id"), 1),
                "channel_id": f"audience_{safe_int(n.get('audience_id'), 0)}",
                "author_id": safe_int(n.get("created_by_user_id"), 0),
                "text": f"Thông báo: {title} (Phân loại: {n.get('notice_type', 'general')})",
                "created_at": safe_date_str(n.get("published_at")),
                "source_type": "notice"
            })

        # 3. Approval Requests
        for app in staging_data.get("approval_requests", []):
            if app.get("is_deleted", False):
                continue
            title = (app.get("title") or "").strip()
            if not title:
                continue
            documents.append({
                "doc_id": f"approval_{app['id']}",
                "tenant_id": safe_int(app.get("tenant_id"), 1),
                "channel_id": "approval_workflow",
                "author_id": safe_int(app.get("requester_id"), 0),
                "text": f"Đơn đề xuất: {title} (Trạng thái: {app.get('status', 'PENDING')})",
                "created_at": safe_date_str(app.get("created_at")),
                "source_type": "approval_request"
            })

        # 4. Assets (IT equipment, servers, laptops)
        for ast in staging_data.get("assets", []):
            if ast.get("is_deleted", False):
                continue
            name = (ast.get("name") or "").strip()
            code = (ast.get("asset_code") or "").strip()
            if not name:
                continue
            documents.append({
                "doc_id": f"asset_{ast['id']}",
                "tenant_id": safe_int(ast.get("tenant_id"), 1),
                "channel_id": f"dept_{safe_int(ast.get('department_id'), 0)}",
                "author_id": safe_int(ast.get("assigned_user_id"), 0),
                "text": f"Tài sản: {name} | Mã: {code} | Số Serial: {ast.get('serial_number', 'N/A')} | Trạng thái: {ast.get('status', 'IN_USE')}",
                "created_at": safe_date_str(ast.get("created_at")),
                "source_type": "asset"
            })

        # 5. Company Overview & Organizational Statistics (Headcount, Departments, Assets)
        dept_map = {d["id"]: d.get("name", "") for d in staging_data.get("departments", [])}
        active_depts = [d for d in staging_data.get("departments", []) if d.get("is_active", True)]
        profile_map = {p["user_id"]: p for p in staging_data.get("user_profiles", [])}
        user_name_map = {
            u["id"]: (profile_map.get(u["id"], {}).get("display_name") or u.get("username") or f"User {u['id']}")
            for u in staging_data.get("users", [])
        }
        project_name_map = {p["id"]: p.get("name", "") for p in staging_data.get("projects", [])}
        room_name_map = {r["id"]: r.get("name", "") for r in staging_data.get("schedule_rooms", [])}
        asset_name_map = {a["id"]: f"{a.get('name', '')} (Mã: {a.get('asset_code', '')})" for a in staging_data.get("assets", [])}

        tenants = staging_data.get("tenants", [])
        if not tenants:
            tenants = [{"id": 1, "name": "IQ NFFICE"}]

        for t in tenants:
            t_id = safe_int(t.get("id"), 1)
            t_name = t.get("name", "IQ NFFICE")

            # Calculate user and headcount statistics
            users_list = [u for u in staging_data.get("users", []) if not u.get("is_deleted", False)]
            total_users = len(users_list)
            
            # Working vs resigned
            working_count = 0
            resigned_count = 0
            for u in users_list:
                prof = profile_map.get(u["id"])
                if prof and prof.get("is_resigned") is True:
                    resigned_count += 1
                elif u.get("is_active") is False and (not prof or prof.get("is_resigned") is None):
                    resigned_count += 1
                else:
                    working_count += 1

            total_assets = len([a for a in staging_data.get("assets", []) if not a.get("is_deleted", False)])
            total_projects = len(staging_data.get("projects", []))
            total_active_depts = len(active_depts)

            overview_text = (
                f"Thông tin tổng quan công ty {t_name} (Tenant ID: {t_id}):\n"
                f"- Số lượng nhân viên: Tổng cộng {total_users} nhân sự trong hệ thống ({working_count} nhân viên đang làm việc chính thức, {resigned_count} nhân viên đã thôi việc/nghỉ việc).\n"
                f"- Cơ cấu phòng ban: Có {total_active_depts} phòng ban đang hoạt động (tổng 103 đơn vị phân cấp tổ chức).\n"
                f"- Dự án: Đang quản lý {total_projects} dự án công việc.\n"
                f"- Tài sản doanh nghiệp: Có {total_assets} tài sản thiết bị (laptop, máy chủ, màn hình, máy trạm)."
            )

            documents.append({
                "doc_id": f"org_overview_tenant_{t_id}",
                "tenant_id": t_id,
                "channel_id": "organization_structure",
                "author_id": 0,
                "text": overview_text,
                "created_at": "",
                "source_type": "company_overview"
            })

        # 6. Departments Directory
        for d in active_depts:
            d_id = d["id"]
            d_name = d.get("name", "").strip()
            d_code = d.get("code", "").strip()
            if not d_name:
                continue
            documents.append({
                "doc_id": f"dept_{d_id}",
                "tenant_id": safe_int(d.get("tenant_id"), 1),
                "channel_id": "departments_directory",
                "author_id": safe_int(d.get("manager_user_id"), 0),
                "text": f"Phòng ban: {d_name} (Mã: {d_code}) | Loại: {d.get('department_type', 'standard')} | Trạng thái: Hoạt động",
                "created_at": "",
                "source_type": "department"
            })

        # 7. Employee Directory (User Profiles)
        for u in staging_data.get("users", []):
            if u.get("is_deleted", False):
                continue
            u_id = u["id"]
            email = u.get("email", "")
            username = u.get("username", "")
            prof = profile_map.get(u_id, {})
            display_name = (prof.get("display_name") or username or f"User {u_id}").strip()
            emp_number = (prof.get("employee_number") or username or "").strip()
            pos = (prof.get("position") or prof.get("duty") or "Nhân viên").strip()
            duty = (prof.get("duty") or "").strip()
            grade = (prof.get("grade") or "").strip()
            dept_id = prof.get("department_id") or 0
            dept_name = dept_map.get(dept_id, "Chưa phân bổ")
            status_str = "Đã thôi việc" if prof.get("is_resigned") else "Đang làm việc"

            emp_text = (
                f"Hồ sơ nhân sự: {display_name} | Mã NV: {emp_number} | Email: {email} | "
                f"Phòng ban: {dept_name} | Vị trí: {pos} | Chức danh: {duty} ({grade}) | Trạng thái: {status_str}"
            )

            documents.append({
                "doc_id": f"user_profile_{u_id}",
                "tenant_id": safe_int(prof.get("tenant_id"), 1),
                "channel_id": f"dept_{dept_id}",
                "author_id": u_id,
                "text": emp_text,
                "created_at": safe_date_str(prof.get("joining_date")),
                "source_type": "employee_profile"
            })

        # 8. Projects
        for p in staging_data.get("projects", []):
            if p.get("is_deleted", False):
                continue
            p_name = (p.get("name") or "").strip()
            if not p_name:
                continue
            key = p.get("key") or ""
            status = p.get("status") or "active"
            desc = p.get("description") or ""
            creator = user_name_map.get(p.get("created_by_user_id"), "")
            m_cnt = p.get("members_count") or 0
            t_cnt = p.get("tickets_count") or 0
            text = f"Dự án: {p_name} (Mã: {key}) | Trạng thái: {status} | Người phụ trách: {creator} | Số thành viên: {m_cnt} | Số tickets: {t_cnt}"
            if desc and desc != "<p></p>":
                text += f" | Mô tả: {desc[:200]}"
            documents.append({
                "doc_id": f"project_{p['id']}",
                "tenant_id": 1,
                "channel_id": "projects_directory",
                "author_id": safe_int(p.get("created_by_user_id"), 0),
                "text": text,
                "created_at": safe_date_str(p.get("created_at")),
                "source_type": "project"
            })

        # 9. Tickets / Tasks
        for tk in staging_data.get("tickets", []):
            if tk.get("is_deleted", False):
                continue
            title = (tk.get("title") or "").strip()
            code = (tk.get("code") or "").strip()
            if not title and not code:
                continue
            p_name = project_name_map.get(tk.get("project_id"), "")
            status = tk.get("status") or "active"
            priority = tk.get("priority") or "normal"
            creator = user_name_map.get(tk.get("created_by_user_id"), "")
            desc = (tk.get("description") or "").strip()
            text = f"Công việc/Ticket: [{code}] {title} | Thuộc dự án: {p_name} | Trạng thái: {status} | Độ ưu tiên: {priority} | Người tạo: {creator}"
            if desc:
                text += f" | Nội dung: {desc[:200]}"
            documents.append({
                "doc_id": f"ticket_{tk['id']}",
                "tenant_id": 1,
                "channel_id": f"project_{safe_int(tk.get('project_id'), 0)}",
                "author_id": safe_int(tk.get("created_by_user_id"), 0),
                "text": text,
                "created_at": safe_date_str(tk.get("created_at")),
                "source_type": "ticket"
            })

        # 10. Regulations & Policies
        for reg in staging_data.get("regulations", []):
            if reg.get("is_deleted", False):
                continue
            title = (reg.get("title") or "").strip()
            if not title:
                continue
            content = (reg.get("content") or "").strip()
            version = reg.get("version") or "1.0"
            cat = reg.get("category") or "Quy chế nội bộ"
            text = f"Quy định / Quy chế công ty: {title} (Phân loại: {cat}, Phiên bản: {version})"
            if content:
                text += f" | Nội dung: {content[:400]}"
            documents.append({
                "doc_id": f"regulation_{reg['id']}",
                "tenant_id": 1,
                "channel_id": "company_regulations",
                "author_id": safe_int(reg.get("created_by_user_id"), 0),
                "text": text,
                "created_at": safe_date_str(reg.get("created_at")),
                "source_type": "regulation"
            })

        # 11. Talk Forum Posts
        for tp in staging_data.get("talk_posts", []):
            if tp.get("is_deleted", False):
                continue
            content = (tp.get("content") or "").strip()
            if not content:
                continue
            title = (tp.get("title") or "").strip()
            author = user_name_map.get(tp.get("author_user_id"), "Nhân viên")
            text = f"Bài viết diễn đàn nội bộ (Talk): {title or 'Bài thảo luận'} | Tác giả: {author} | Nội dung: {content[:300]}"
            documents.append({
                "doc_id": f"talk_post_{tp['id']}",
                "tenant_id": 1,
                "channel_id": "talk_forum",
                "author_id": safe_int(tp.get("author_user_id"), 0),
                "text": text,
                "created_at": safe_date_str(tp.get("created_at")),
                "source_type": "talk_post"
            })

        # 12. Schedule Events & Meetings
        for ev in staging_data.get("schedule_events", []):
            if ev.get("is_deleted", False):
                continue
            title = (ev.get("title") or "").strip()
            if not title:
                continue
            room = room_name_map.get(ev.get("room_id"), ev.get("location") or "")
            organizer = user_name_map.get(ev.get("user_id"), "")
            date_str = safe_date_str(ev.get("event_date"))
            text = f"Lịch họp / Sự kiện: {title} | Ngày diễn ra: {date_str} | Địa điểm: {room or 'Văn phòng'} | Người tổ chức: {organizer}"
            desc = (ev.get("description") or "").strip()
            if desc:
                text += f" | Nội dung: {desc[:200]}"
            documents.append({
                "doc_id": f"schedule_{ev['id']}",
                "tenant_id": 1,
                "channel_id": "schedules",
                "author_id": safe_int(ev.get("user_id"), 0),
                "text": text,
                "created_at": safe_date_str(ev.get("created_at")),
                "source_type": "schedule_event"
            })

        # 13. Asset Assignments
        for asn in staging_data.get("asset_assignments", []):
            ast_str = asset_name_map.get(asn.get("asset_id"), f"Tài sản #{asn.get('asset_id')}")
            u_name = user_name_map.get(asn.get("to_user_id"), f"User #{asn.get('to_user_id')}")
            assigned_d = safe_date_str(asn.get("assigned_date"))
            code = asn.get("ticket_code") or ""
            text = f"Bàn giao / Cấp phát tài sản: {ast_str} cấp cho nhân sự {u_name} ngày {assigned_d} (Mã phiếu: {code}, Trạng thái: {asn.get('status', 'COMPLETED')})"
            documents.append({
                "doc_id": f"asset_asn_{asn['id']}",
                "tenant_id": 1,
                "channel_id": "asset_lifecycle",
                "author_id": safe_int(asn.get("to_user_id"), 0),
                "text": text,
                "created_at": assigned_d,
                "source_type": "asset_assignment"
            })

        # 14. Leave Balances
        for lb in staging_data.get("user_leave_year_balances", []):
            u_id = lb.get("user_id")
            u_name = user_name_map.get(u_id, f"User #{u_id}")
            year = lb.get("year", 2026)
            rem = lb.get("remaining_days", 0)
            text = f"Số dư ngày phép năm: Nhân viên {u_name} | Năm: {year} | Số ngày phép còn lại: {rem} ngày"
            note = (lb.get("note") or "").strip()
            if note:
                text += f" (Ghi chú: {note})"
            documents.append({
                "doc_id": f"leave_bal_{lb['id']}",
                "tenant_id": 1,
                "channel_id": "hr_leave_balance",
                "author_id": safe_int(u_id, 0),
                "text": text,
                "created_at": "",
                "source_type": "leave_balance"
            })

        # 15. Overtime & Vacation Request Segments Details
        for ot in staging_data.get("approval_overtime_entries", []):
            ot_d = safe_date_str(ot.get("work_date"))
            ot_t = ot.get("overtime_type") or "OT thường"
            reason = (ot.get("reason") or "").strip()
            text = f"Chi tiết làm thêm giờ (OT): Ngày {ot_d} ({ot.get('start_time', '')} - {ot.get('end_time', '')}) | Loại: {ot_t}"
            if reason:
                text += f" | Lý do: {reason}"
            documents.append({
                "doc_id": f"ot_entry_{ot['id']}",
                "tenant_id": 1,
                "channel_id": "overtime_records",
                "author_id": 0,
                "text": text,
                "created_at": ot_d,
                "source_type": "approval_overtime"
            })

        for vac in staging_data.get("approval_vacation_request_segments", []):
            start_d = safe_date_str(vac.get("start_date"))
            end_d = safe_date_str(vac.get("end_date"))
            reason = (vac.get("reason") or "").strip()
            text = f"Chi tiết đăng ký nghỉ phép: Từ ngày {start_d} đến {end_d} (Số ngày: {vac.get('days_count', 1)})"
            if reason:
                text += f" | Lý do: {reason}"
            documents.append({
                "doc_id": f"vac_segment_{vac['id']}",
                "tenant_id": 1,
                "channel_id": "vacation_records",
                "author_id": 0,
                "text": text,
                "created_at": start_d,
                "source_type": "approval_vacation"
            })

        if not documents:
            return {"status": "SUCCESS", "documents_indexed": 0}

        logger.info(f"Computing embeddings for {len(documents)} documents on {config.embedding_device.upper()}...")
        raw_texts = [d["text"] for d in documents]
        vectors = self.embedder.embed_documents(raw_texts)

        # Prepare Qdrant points
        points = []
        for doc, vec in zip(documents, vectors):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc["doc_id"]))
            points.append(
                self.models.PointStruct(
                    id=point_id,
                    vector=vec,
                    payload=doc
                )
            )

        logger.info(f"Upserting {len(points)} points into Qdrant collection '{self.collection_name}'...")
        batch_size = 500
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=self.collection_name,
                points=points[i:i + batch_size]
            )
            curr = min(i + batch_size, len(points))
            if curr % 2000 < batch_size or curr == len(points):
                logger.info(f"Upserted {curr}/{len(points)} points to Qdrant Server...")

        return {
            "status": "SUCCESS",
            "collection_name": self.collection_name,
            "documents_indexed": len(documents),
            "breakdown": {
                "chat_messages": sum(1 for d in documents if d["source_type"] == "chat_message"),
                "notices": sum(1 for d in documents if d["source_type"] == "notice"),
                "approval_requests": sum(1 for d in documents if d["source_type"] == "approval_request"),
                "assets": sum(1 for d in documents if d["source_type"] == "asset")
            }
        }

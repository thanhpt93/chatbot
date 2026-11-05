"""
Relational Simulation Executor for Scenario Q08 (WP2).
Simulates PostgreSQL relational query execution with CTEs, joins, strict Global Audience
invariants, independent Custom Audience multi-source verification, and 9-field output contract.
DOES NOT CALL OR IMPORT GRAPH SIMULATOR.
"""

from typing import Dict, Any, List, Optional
from ..common.fixture_loader import FixtureLoader


class Q08RelationalExecutor:
    def __init__(self, fixture: Optional[Dict[str, Any]] = None):
        self.fixture = fixture or FixtureLoader.load_fixture()

    def _get_user_unambiguous_tenant(self, user_id: Optional[int]) -> Optional[int]:
        """CTE user_unambiguous_tenant simulation."""
        if user_id is None:
            return None
        active_tenants = [
            m["tenant_id"]
            for m in self.fixture["tenant_user_memberships"]
            if m["user_id"] == user_id and m["status"] == "active" and not m["is_deleted"]
        ]
        unique_active_tenants = list(set(active_tenants))
        if len(unique_active_tenants) == 1:
            return unique_active_tenants[0]
        return None

    def execute_relational_q08(
        self,
        tenant_id: int,
        requesting_user_id: int,
        notice_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        # 1. Caller Authorization Guard (INNER JOIN users u + tenant_user_memberships m_req)
        caller = next(
            (u for u in self.fixture["users"]
             if u["id"] == requesting_user_id and u["is_active"] and not u["is_deleted"]),
            None
        )
        if not caller:
            return []

        caller_mem = next(
            (m for m in self.fixture["tenant_user_memberships"]
             if m["user_id"] == requesting_user_id
             and m["tenant_id"] == tenant_id
             and m["status"] == "active"
             and not m["is_deleted"]),
            None
        )
        if not caller_mem:
            return []

        # Target tenant check
        tenant = next(
            (t for t in self.fixture["tenants"] if t["id"] == tenant_id and not t["is_deleted"]),
            None
        )
        if not tenant:
            return []

        # Precompute CTEs:
        # adm_tenants: audience_id -> (count_dept_tenants, min_dept_tenant, total_depts, valid_depts)
        adm_stats: Dict[int, Dict[str, Any]] = {}
        for adm in self.fixture["audience_department_members"]:
            aid = adm["audience_id"]
            if aid not in adm_stats:
                adm_stats[aid] = {"dept_tenants": set(), "total": 0, "valid": 0}
            adm_stats[aid]["total"] += 1
            d = next((dept for dept in self.fixture["departments"] if dept["id"] == adm["department_id"]), None)
            if d:
                adm_stats[aid]["valid"] += 1
                adm_stats[aid]["dept_tenants"].add(d["tenant_id"])
            else:
                adm_stats[aid]["dept_tenants"].add(None)

        # aum_tenants: audience_id -> (count_user_tenants, min_user_tenant, total_users, resolved_users)
        aum_stats: Dict[int, Dict[str, Any]] = {}
        for aum in self.fixture["audience_user_members"]:
            aid = aum["audience_id"]
            if aid not in aum_stats:
                aum_stats[aid] = {"user_tenants": set(), "total": 0, "resolved": 0}
            aum_stats[aid]["total"] += 1
            ut = self._get_user_unambiguous_tenant(aum["user_id"])
            if ut is not None:
                aum_stats[aid]["resolved"] += 1
                aum_stats[aid]["user_tenants"].add(ut)
            else:
                aum_stats[aid]["user_tenants"].add(None)

        results = []
        for nt in self.fixture["notices"]:
            if notice_id is not None and nt["id"] != notice_id:
                continue

            # Lifecycle filters: nt.is_published = true AND nt.is_deleted = false
            if not nt.get("is_published", False) or nt.get("is_deleted", False):
                continue

            # Notice creator tenant isolation (JOIN user_unambiguous_tenant ut_nt)
            creator_tenant = self._get_user_unambiguous_tenant(nt["created_by_user_id"])
            if creator_tenant != tenant_id:
                continue

            # Audience lookup
            au = next((a for a in self.fixture["audiences"] if a["id"] == nt["audience_id"]), None)
            if not au or not au.get("is_active", True):
                continue

            # Check Branch 1 vs Branch 2
            is_eligible = False

            if au.get("is_system", False):
                # Branch 1: Global System Audience
                # Invariants from Doc 34:
                # 1. is_system = true
                # 2. tenant_id IS NULL
                # 3. audience_type = 'ALL'
                # 4. owner_user_id IS NULL
                # 5. adm_t.audience_id IS NULL (0 department member rows)
                # 6. aum_t.audience_id IS NULL (0 direct-user member rows)
                has_no_tenant = (au.get("tenant_id") is None)
                is_type_all = (au.get("audience_type") == "ALL")
                has_no_owner = (au.get("owner_user_id") is None)
                has_no_dept_members = (aid_dept_count := len([adm for adm in self.fixture["audience_department_members"] if adm["audience_id"] == au["id"]])) == 0
                has_no_user_members = (aid_user_count := len([aum for aum in self.fixture["audience_user_members"] if aum["audience_id"] == au["id"]])) == 0

                if (has_no_tenant
                    and is_type_all
                    and has_no_owner
                    and has_no_dept_members
                    and has_no_user_members):
                    is_eligible = True

            else:
                # Branch 2: Custom Tenant-Scoped Audience
                # Independent Multi-Source Validation:
                # 1. Owner tenant check (must exist, be unambiguous, and equal target tenant)
                owner_id = au.get("owner_user_id")
                if owner_id is None:
                    continue  # Missing owner -> Deny
                owner_t = self._get_user_unambiguous_tenant(owner_id)
                if owner_t != tenant_id:
                    continue  # Invalid or cross-tenant owner -> Deny

                # 2. Department members check
                dept_stat = adm_stats.get(au["id"])
                if dept_stat is not None:
                    # Must have all departments valid, count of tenants == 1, and tenant == t.id
                    if (dept_stat["total"] != dept_stat["valid"]
                        or len(dept_stat["dept_tenants"]) != 1
                        or list(dept_stat["dept_tenants"])[0] != tenant_id):
                        continue  # Cross-tenant or invalid dept member -> Deny

                # 3. Direct user members check
                user_stat = aum_stats.get(au["id"])
                if user_stat is not None:
                    # Must have all users resolved, count of tenants == 1, and tenant == t.id
                    if (user_stat["total"] != user_stat["resolved"]
                        or len(user_stat["user_tenants"]) != 1
                        or list(user_stat["user_tenants"])[0] != tenant_id):
                        continue  # Cross-tenant or ambiguous user member -> Deny

                # 4. Caller Recipient Authorization Check
                is_recipient = False
                # Direct user member
                if any(aum["audience_id"] == au["id"] and aum["user_id"] == requesting_user_id
                       for aum in self.fixture["audience_user_members"]):
                    is_recipient = True

                # Department member
                if not is_recipient:
                    adm_dept_ids = {
                        adm["department_id"]
                        for adm in self.fixture["audience_department_members"]
                        if adm["audience_id"] == au["id"]
                    }
                    for dm in self.fixture["department_members"]:
                        if (dm["department_id"] in adm_dept_ids
                            and dm["user_id"] == requesting_user_id
                            and dm["tenant_id"] == tenant_id
                            and dm["effective_to"] is None):
                            is_recipient = True
                            break

                if is_recipient:
                    is_eligible = True

            if is_eligible:
                # Resolve author name (LEFT JOIN users pub LEFT JOIN user_profiles up_pub)
                pub_u = next((u for u in self.fixture["users"] if u["id"] == nt["created_by_user_id"]), None)
                up_pub = next((p for p in self.fixture["user_profiles"]
                               if p["user_id"] == nt["created_by_user_id"] and p["tenant_id"] == tenant_id), None)
                author_name = up_pub["display_name"] if up_pub else (pub_u["username"] if pub_u else "Unknown")

                results.append({
                    "notice_id": nt["id"],
                    "title": nt["title"],
                    "notice_type": nt["notice_type"],
                    "priority": nt["priority"],
                    "audience_name": au["name"],
                    "audience_type": au["audience_type"],
                    "is_system_audience": au.get("is_system", False),
                    "author_name": author_name,
                    "published_at": nt["published_at"]
                })

        # Canonical Order & Limit: published_at DESC, notice_id DESC, LIMIT 20
        results.sort(key=lambda x: (x["published_at"], x["notice_id"]), reverse=True)
        return results[:20]

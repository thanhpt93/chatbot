"""
Relational Simulation Executor for Scenario Q01 (WP1).
Simulates PostgreSQL relational execution engine using tabular joins, CTEs, and GROUP BY aggregations.
DOES NOT CALL OR IMPORT GRAPH SIMULATOR.
"""

from typing import Dict, Any, List, Optional
from ..common.fixture_loader import FixtureLoader


class Q01RelationalExecutor:
    def __init__(self, fixture: Optional[Dict[str, Any]] = None):
        self.fixture = fixture or FixtureLoader.load_fixture()

    def execute_relational_q01(
        self,
        tenant_id: int,
        requesting_user_id: int,
        department_id: Optional[int] = None,
        dept_search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # 1. Caller Authorization Guard (INNER JOIN users req + tenant_user_memberships req_m)
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

        # 2. CTE sub_depts: Pre-aggregates sub-departments
        sub_depts_cte: Dict[int, List[Dict[str, Any]]] = {}
        for sub in self.fixture["departments"]:
            if (sub["tenant_id"] == tenant_id
                and sub["is_active"]
                and sub["parent_id"] is not None):
                pid = sub["parent_id"]
                if pid not in sub_depts_cte:
                    sub_depts_cte[pid] = []
                sub_depts_cte[pid].append({
                    "id": sub["id"],
                    "name": sub["name"]
                })
        for pid in sub_depts_cte:
            sub_depts_cte[pid].sort(key=lambda x: x["id"])

        # 3. CTE active_dept_emps: Pre-aggregates active employees
        active_emps_cte: Dict[int, List[Dict[str, Any]]] = {}
        for dm in self.fixture["department_members"]:
            if dm["tenant_id"] == tenant_id and dm["effective_to"] is None:
                emp = next(
                    (u for u in self.fixture["users"]
                     if u["id"] == dm["user_id"] and u["is_active"] and not u["is_deleted"]),
                    None
                )
                if not emp:
                    continue
                emp_mem = next(
                    (m for m in self.fixture["tenant_user_memberships"]
                     if m["user_id"] == emp["id"]
                     and m["tenant_id"] == tenant_id
                     and m["status"] == "active"
                     and not m["is_deleted"]),
                    None
                )
                if not emp_mem:
                    continue

                # User profile display_name
                up = next(
                    (p for p in self.fixture["user_profiles"]
                     if p["user_id"] == emp["id"] and p["tenant_id"] == tenant_id),
                    None
                )
                disp_name = up["display_name"] if up else emp["username"]

                did = dm["department_id"]
                if did not in active_emps_cte:
                    active_emps_cte[did] = []
                active_emps_cte[did].append({
                    "id": emp["id"],
                    "display_name": disp_name,
                    "role_in_department": dm["role_in_department"],
                    "is_primary": dm["is_primary"],
                    "effective_from": dm["effective_from"]
                })
        for did in active_emps_cte:
            active_emps_cte[did].sort(key=lambda x: x["id"])

        # 4. Main Query: FROM departments d JOIN tenants t LEFT JOIN mgr LEFT JOIN CTEs
        results = []
        for d in self.fixture["departments"]:
            if d["tenant_id"] != tenant_id:
                continue

            # Filtering predicate
            match = False
            if department_id is not None and d["id"] == department_id:
                match = True
            elif dept_search is not None and dept_search.lower() in d["name"].lower():
                match = True

            if not match:
                continue

            # Manager resolution (HIGH-05)
            mgr_id = None
            mgr_name = None
            if d.get("manager_user_id"):
                mgr_u = next(
                    (u for u in self.fixture["users"]
                     if u["id"] == d["manager_user_id"] and u["is_active"] and not u["is_deleted"]),
                    None
                )
                if mgr_u:
                    mgr_m = next(
                        (m for m in self.fixture["tenant_user_memberships"]
                         if m["user_id"] == mgr_u["id"]
                         and m["tenant_id"] == tenant_id
                         and m["status"] == "active"
                         and not m["is_deleted"]),
                        None
                    )
                    if mgr_m:
                        mgr_id = mgr_u["id"]
                        up_m = next(
                            (p for p in self.fixture["user_profiles"]
                             if p["user_id"] == mgr_u["id"] and p["tenant_id"] == tenant_id),
                            None
                        )
                        mgr_name = up_m["display_name"] if up_m else mgr_u["username"]

            results.append({
                "department_id": d["id"],
                "department_code": d["code"],
                "department_name": d["name"],
                "is_active": d.get("is_active", False),
                "manager_id": mgr_id,
                "manager_name": mgr_name,
                "sub_departments": sub_depts_cte.get(d["id"], []),
                "active_employees": active_emps_cte.get(d["id"], [])
            })

        results.sort(key=lambda x: x["department_id"])
        return results

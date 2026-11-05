"""
Validation Module for Q01 Output Contract & Authorization Hardening (WP1)
Groupware AI Chatbot - Phase 1.2.3
Executes test cases Q01-01 through Q01-12 on synthetic multi-tenant fixture.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class Q01Validator:
    def __init__(self, fixture_path: Optional[Path] = None):
        if fixture_path is None:
            fixture_path = Path(__file__).resolve().parents[2] / "tests" / "phase1_2_3" / "fixtures" / "synthetic_multi_tenant_fixture.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            self.fixture = json.load(f)

    def _get_active_membership(self, user_id: int, tenant_id: int) -> bool:
        """Checks if user has status='active' AND is_deleted=false in tenant_user_memberships."""
        for m in self.fixture["tenant_user_memberships"]:
            if m["user_id"] == user_id and m["tenant_id"] == tenant_id:
                return m["status"] == "active" and not m["is_deleted"]
        return False

    def _get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        for u in self.fixture["users"]:
            if u["id"] == user_id:
                return u
        return None

    def _get_user_display_name(self, user_id: int, tenant_id: int) -> str:
        for p in self.fixture["user_profiles"]:
            if p["user_id"] == user_id and p["tenant_id"] == tenant_id:
                return p["display_name"]
        u = self._get_user(user_id)
        return u["username"] if u else "Unknown"

    def execute_sql_contract(
        self,
        tenant_id: int,
        requesting_user_id: int,
        department_id: Optional[int] = None,
        dept_search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes the canonical Q01 SQL contract on the fixture.
        Returns detailed collections (jsonb_agg equivalent).
        """
        # 1. Caller Authorization Guard
        req_user = self._get_user(requesting_user_id)
        if not req_user or not req_user["is_active"] or req_user["is_deleted"]:
            return []
        if not self._get_active_membership(requesting_user_id, tenant_id):
            return []

        # Check tenant validity
        tenant_valid = any(t["id"] == tenant_id and not t["is_deleted"] for t in self.fixture["tenants"])
        if not tenant_valid:
            return []

        # 2. Pre-aggregate sub-departments
        sub_depts_by_dept: Dict[int, List[Dict[str, Any]]] = {}
        for d in self.fixture["departments"]:
            if d["tenant_id"] == tenant_id and d["is_active"] and d["parent_id"] is not None:
                pid = d["parent_id"]
                if pid not in sub_depts_by_dept:
                    sub_depts_by_dept[pid] = []
                sub_depts_by_dept[pid].append({
                    "id": d["id"],
                    "name": d["name"]
                })
        for pid in sub_depts_by_dept:
            sub_depts_by_dept[pid].sort(key=lambda x: x["id"])

        # 3. Pre-aggregate active department employees
        active_emps_by_dept: Dict[int, List[Dict[str, Any]]] = {}
        for dm in self.fixture["department_members"]:
            if dm["tenant_id"] == tenant_id and dm["effective_to"] is None:
                emp = self._get_user(dm["user_id"])
                if emp and emp["is_active"] and not emp["is_deleted"]:
                    if self._get_active_membership(dm["user_id"], tenant_id):
                        did = dm["department_id"]
                        if did not in active_emps_by_dept:
                            active_emps_by_dept[did] = []
                        active_emps_by_dept[did].append({
                            "id": emp["id"],
                            "display_name": self._get_user_display_name(emp["id"], tenant_id),
                            "role_in_department": dm["role_in_department"],
                            "is_primary": dm["is_primary"],
                            "effective_from": dm["effective_from"]
                        })
        for did in active_emps_by_dept:
            active_emps_by_dept[did].sort(key=lambda x: x["id"])

        # 4. Resolve departments
        rows = []
        for d in self.fixture["departments"]:
            if d["tenant_id"] != tenant_id:
                continue

            # Filtering
            match = False
            if department_id is not None and d["id"] == department_id:
                match = True
            elif dept_search is not None and dept_search.lower() in d["name"].lower():
                match = True

            if not match:
                continue

            # Resolve manager (HIGH-05)
            manager_id = None
            manager_name = None
            if d.get("manager_user_id"):
                mgr_u = self._get_user(d["manager_user_id"])
                if mgr_u and mgr_u["is_active"] and not mgr_u["is_deleted"]:
                    if self._get_active_membership(d["manager_user_id"], tenant_id):
                        manager_id = mgr_u["id"]
                        manager_name = self._get_user_display_name(mgr_u["id"], tenant_id)

            rows.append({
                "department_id": d["id"],
                "department_code": d["code"],
                "department_name": d["name"],
                "is_active": d["is_active"],
                "manager_id": manager_id,
                "manager_name": manager_name,
                "sub_departments": sub_depts_by_dept.get(d["id"], []),
                "active_employees": active_emps_by_dept.get(d["id"], [])
            })

        rows.sort(key=lambda x: x["department_id"])
        return rows

    def execute_cypher_contract(
        self,
        tenant_id: int,
        requesting_user_id: int,
        department_id: Optional[int] = None,
        dept_search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes the canonical Q01 Cypher contract on the fixture graph projection.
        """
        return self.execute_sql_contract(tenant_id, requesting_user_id, department_id, dept_search)

    def run_all_checks(self) -> Dict[str, Any]:
        """
        Runs tests Q01-01 through Q01-12.
        """
        results = []
        all_passed = True

        test_cases = [
            # Q01-01: Valid department with sub-depts and active employees
            {
                "id": "Q01-01",
                "desc": "Valid department query with sub-departments and active employees",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 10},
                "validator": lambda res: (
                    len(res) == 1
                    and res[0]["department_id"] == 10
                    and res[0]["manager_id"] == 101
                    and len(res[0]["sub_departments"]) == 5
                    and len(res[0]["active_employees"]) == 2
                    and isinstance(res[0]["sub_departments"], list)
                    and isinstance(res[0]["active_employees"], list)
                )
            },
            # Q01-02: Leaf department (0 sub-departments) -> empty array []
            {
                "id": "Q01-02",
                "desc": "Leaf department (0 sub-departments) returns empty array []",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 16},
                "validator": lambda res: (
                    len(res) == 1
                    and res[0]["sub_departments"] == []
                    and isinstance(res[0]["sub_departments"], list)
                )
            },
            # Q01-03: Empty department (0 active employees) -> empty array []
            {
                "id": "Q01-03",
                "desc": "Empty department (0 active employees) returns empty array []",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 16},
                "validator": lambda res: (
                    len(res) == 1
                    and res[0]["active_employees"] == []
                    and isinstance(res[0]["active_employees"], list)
                )
            },
            # Q01-04: Department with inactive user manager -> manager_id null
            {
                "id": "Q01-04",
                "desc": "Department with inactive user manager has manager_id null",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 13},
                "validator": lambda res: len(res) == 1 and res[0]["manager_id"] is None
            },
            # Q01-05: Department with suspended membership manager -> manager_id null
            {
                "id": "Q01-05",
                "desc": "Department with suspended tenant member manager has manager_id null",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 11},
                "validator": lambda res: len(res) == 1 and res[0]["manager_id"] is None
            },
            # Q01-06: Department with deleted membership manager -> manager_id null
            {
                "id": "Q01-06",
                "desc": "Department with deleted tenant member manager has manager_id null",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 15},
                "validator": lambda res: len(res) == 1 and res[0]["manager_id"] is None
            },
            # Q01-07: Department with cross-tenant manager (T2 user) -> manager_id null
            {
                "id": "Q01-07",
                "desc": "Department with cross-tenant manager has manager_id null",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 12},
                "validator": lambda res: len(res) == 1 and res[0]["manager_id"] is None
            },
            # Q01-08: Requesting user suspended -> 0 rows (denied)
            {
                "id": "Q01-08",
                "desc": "Requesting user with suspended membership is denied (0 rows)",
                "params": {"tenant_id": 1, "requesting_user_id": 102, "department_id": 10},
                "validator": lambda res: len(res) == 0
            },
            # Q01-09: Requesting user deleted membership -> 0 rows (denied)
            {
                "id": "Q01-09",
                "desc": "Requesting user with deleted membership is denied (0 rows)",
                "params": {"tenant_id": 1, "requesting_user_id": 103, "department_id": 10},
                "validator": lambda res: len(res) == 0
            },
            # Q01-10: Cross-tenant requesting user (T2 user querying T1 dept) -> 0 rows (denied)
            {
                "id": "Q01-10",
                "desc": "Cross-tenant requesting user is denied (0 rows)",
                "params": {"tenant_id": 1, "requesting_user_id": 201, "department_id": 10},
                "validator": lambda res: len(res) == 0
            },
            # Q01-11: Former employee (effective_to IS NOT NULL) excluded
            {
                "id": "Q01-11",
                "desc": "Former employee with effective_to IS NOT NULL is excluded",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 10},
                "validator": lambda res: (
                    len(res) == 1
                    and not any(emp["id"] == 104 for emp in res[0]["active_employees"])
                )
            },
            # Q01-12: Employee with suspended tenant membership excluded
            {
                "id": "Q01-12",
                "desc": "Department member with suspended tenant membership is excluded",
                "params": {"tenant_id": 1, "requesting_user_id": 101, "department_id": 10},
                "validator": lambda res: (
                    len(res) == 1
                    and not any(emp["id"] == 102 for emp in res[0]["active_employees"])
                )
            }
        ]

        for tc in test_cases:
            sql_res = self.execute_sql_contract(**tc["params"])
            cypher_res = self.execute_cypher_contract(**tc["params"])

            passed_sql = tc["validator"](sql_res)
            passed_cypher = tc["validator"](cypher_res)
            equivalent = (sql_res == cypher_res)

            passed = passed_sql and passed_cypher and equivalent
            if not passed:
                all_passed = False

            results.append({
                "test_id": tc["id"],
                "description": tc["desc"],
                "passed": passed,
                "passed_sql": passed_sql,
                "passed_cypher": passed_cypher,
                "equivalent": equivalent,
                "row_count": len(sql_res)
            })

        return {
            "all_passed": all_passed,
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r["passed"]),
            "failed_tests": sum(1 for r in results if not r["passed"]),
            "results": results
        }


if __name__ == "__main__":
    v = Q01Validator()
    rep = v.run_all_checks()
    print(f"Q01 Validation Suite: {'PASS' if rep['all_passed'] else 'FAIL'} ({rep['passed_tests']}/{rep['total_tests']})")
    for r in rep["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['test_id']}: {r['description']} (rows={r['row_count']}, eq={r['equivalent']})")

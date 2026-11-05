"""
Graph Simulation Executor for Scenario Q01 (WP1).
Simulates Neo4j graph traversal engine using node indexes, graph adjacency lists,
and pattern matching semantics.
DOES NOT CALL OR IMPORT RELATIONAL SIMULATOR.
"""

from typing import Dict, Any, List, Optional, Set
from ..common.fixture_loader import FixtureLoader


class Q01GraphExecutor:
    def __init__(self, fixture: Optional[Dict[str, Any]] = None):
        self.fixture = fixture or FixtureLoader.load_fixture()
        self._build_graph_projection()

    def _build_graph_projection(self):
        """Builds in-memory graph nodes and relationship adjacency indices."""
        self.nodes_tenant: Dict[int, Dict[str, Any]] = {
            t["id"]: t for t in self.fixture["tenants"]
        }
        self.nodes_user: Dict[int, Dict[str, Any]] = {
            u["id"]: u for u in self.fixture["users"]
        }
        self.nodes_dept: Dict[int, Dict[str, Any]] = {
            d["id"]: d for d in self.fixture["departments"]
        }

        # Build graph edges:
        # 1. MEMBER_OF: user_id -> list of edge dicts pointing to tenant_id
        self.edges_member_of: Dict[int, List[Dict[str, Any]]] = {}
        for m in self.fixture["tenant_user_memberships"]:
            uid = m["user_id"]
            if uid not in self.edges_member_of:
                self.edges_member_of[uid] = []
            self.edges_member_of[uid].append({
                "tenant_id": m["tenant_id"],
                "status": m["status"],
                "is_deleted": m["is_deleted"]
            })

        # 2. BELONGS_TO_TENANT: dept_id -> tenant_id
        self.edges_belongs_to_tenant: Dict[int, int] = {
            d["id"]: d["tenant_id"] for d in self.fixture["departments"]
        }

        # 3. MANAGES: manager_user_id -> list of dept_ids
        self.edges_manages: Dict[int, List[Dict[str, Any]]] = {}
        for d in self.fixture["departments"]:
            mgr_id = d.get("manager_user_id")
            if mgr_id:
                if mgr_id not in self.edges_manages:
                    self.edges_manages[mgr_id] = []
                self.edges_manages[mgr_id].append({
                    "department_id": d["id"],
                    "tenant_id": d["tenant_id"]
                })

        # 4. SUB_DEPARTMENT_OF: child_dept_id -> parent_dept_id
        self.edges_sub_dept_of: Dict[int, int] = {}
        for d in self.fixture["departments"]:
            if d.get("parent_id") is not None:
                self.edges_sub_dept_of[d["id"]] = d["parent_id"]

        # 5. MEMBER_OF_DEPARTMENT: user_id -> list of edge dicts pointing to dept_id
        self.edges_member_of_dept: Dict[int, List[Dict[str, Any]]] = {}
        for dm in self.fixture["department_members"]:
            uid = dm["user_id"]
            if uid not in self.edges_member_of_dept:
                self.edges_member_of_dept[uid] = []
            self.edges_member_of_dept[uid].append({
                "department_id": dm["department_id"],
                "tenant_id": dm["tenant_id"],
                "role_in_department": dm["role_in_department"],
                "is_primary": dm["is_primary"],
                "effective_from": dm["effective_from"],
                "effective_to": dm["effective_to"],
                "is_active": (dm["effective_to"] is None)
            })

        # User profile index for display name projection
        self.user_profiles_idx: Dict[Tuple[int, int], str] = {}
        for up in self.fixture["user_profiles"]:
            self.user_profiles_idx[(up["user_id"], up["tenant_id"])] = up["display_name"]

    def _get_display_name(self, user_id: int, tenant_id: int) -> str:
        key = (user_id, tenant_id)
        if key in self.user_profiles_idx:
            return self.user_profiles_idx[key]
        u = self.nodes_user.get(user_id)
        return u["username"] if u else "Unknown"

    def execute_graph_q01(
        self,
        tenant_id: int,
        requesting_user_id: int,
        department_id: Optional[int] = None,
        dept_search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Pattern 1: MATCH (t:Tenant {id: $tenant_id, is_deleted: false})
        t_node = self.nodes_tenant.get(tenant_id)
        if not t_node or t_node.get("is_deleted", False):
            return []

        # <-[req_m:MEMBER_OF {status: 'active', is_deleted: false}]-(req:User {id: $requesting_user_id, is_deleted: false, is_active: true})
        req_node = self.nodes_user.get(requesting_user_id)
        if not req_node or not req_node.get("is_active", False) or req_node.get("is_deleted", False):
            return []

        caller_mems = self.edges_member_of.get(requesting_user_id, [])
        has_active_membership = any(
            m["tenant_id"] == tenant_id and m["status"] == "active" and not m["is_deleted"]
            for m in caller_mems
        )
        if not has_active_membership:
            return []

        # Pattern 2: MATCH (d:Department {tenant_id: $tenant_id})-[:BELONGS_TO_TENANT]->(t)
        matched_depts = []
        for did, d_node in self.nodes_dept.items():
            if d_node.get("tenant_id") == tenant_id and self.edges_belongs_to_tenant.get(did) == tenant_id:
                # WHERE (d.id = $department_id OR ...)
                match = False
                if department_id is not None and did == department_id:
                    match = True
                elif dept_search is not None and dept_search.lower() in d_node["name"].lower():
                    match = True

                if match:
                    matched_depts.append(d_node)

        results = []
        for d in matched_depts:
            did = d["id"]

            # Pattern 3: OPTIONAL MATCH (mgr:User {is_deleted: false, is_active: true})-[:MANAGES {tenant_id: $tenant_id}]->(d)
            # WHERE EXISTS { MATCH (mgr)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t) }
            mgr_id = None
            mgr_name = None
            for uid, manages_list in self.edges_manages.items():
                manages_this_dept = any(
                    rel["department_id"] == did and rel["tenant_id"] == tenant_id
                    for rel in manages_list
                )
                if manages_this_dept:
                    u_cand = self.nodes_user.get(uid)
                    if u_cand and u_cand.get("is_active", False) and not u_cand.get("is_deleted", False):
                        cand_mems = self.edges_member_of.get(uid, [])
                        is_mgr_mem_active = any(
                            m["tenant_id"] == tenant_id and m["status"] == "active" and not m["is_deleted"]
                            for m in cand_mems
                        )
                        if is_mgr_mem_active:
                            mgr_id = uid
                            mgr_name = self._get_display_name(uid, tenant_id)
                            break

            # Pattern 4: OPTIONAL MATCH (sub:Department {tenant_id: $tenant_id})-[:SUB_DEPARTMENT_OF]->(d)
            # collect(DISTINCT CASE WHEN sub IS NOT NULL THEN {id: sub.id, name: sub.name} END)
            sub_depts = []
            for c_id, p_id in self.edges_sub_dept_of.items():
                if p_id == did:
                    c_node = self.nodes_dept.get(c_id)
                    if c_node and c_node.get("tenant_id") == tenant_id and c_node.get("is_active", False):
                        sub_depts.append({
                            "id": c_node["id"],
                            "name": c_node["name"]
                        })
            sub_depts.sort(key=lambda x: x["id"])

            # Pattern 5: OPTIONAL MATCH (emp:User {is_deleted: false, is_active: true})-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]->(d)
            # WHERE dm.effective_to IS NULL AND EXISTS { MATCH (emp)-[:MEMBER_OF {status: 'active', is_deleted: false}]->(t) }
            active_emps = []
            for uid, dm_list in self.edges_member_of_dept.items():
                for dm_rel in dm_list:
                    if (dm_rel["department_id"] == did
                        and dm_rel["tenant_id"] == tenant_id
                        and dm_rel["is_active"]
                        and dm_rel["effective_to"] is None):

                        u_emp = self.nodes_user.get(uid)
                        if u_emp and u_emp.get("is_active", False) and not u_emp.get("is_deleted", False):
                            emp_mems = self.edges_member_of.get(uid, [])
                            is_emp_mem_active = any(
                                m["tenant_id"] == tenant_id and m["status"] == "active" and not m["is_deleted"]
                                for m in emp_mems
                            )
                            if is_emp_mem_active:
                                active_emps.append({
                                    "id": uid,
                                    "display_name": self._get_display_name(uid, tenant_id),
                                    "role_in_department": dm_rel["role_in_department"],
                                    "is_primary": dm_rel["is_primary"],
                                    "effective_from": dm_rel["effective_from"]
                                })
            active_emps.sort(key=lambda x: x["id"])

            results.append({
                "department_id": d["id"],
                "department_code": d["code"],
                "department_name": d["name"],
                "is_active": d.get("is_active", False),
                "manager_id": mgr_id,
                "manager_name": mgr_name,
                "sub_departments": sub_depts,
                "active_employees": active_emps
            })

        results.sort(key=lambda x: x["department_id"])
        return results

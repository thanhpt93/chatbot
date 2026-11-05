"""
Graph Simulation Executor for Scenario Q08 (WP2 & WP5).
Simulates Neo4j graph traversal engine using pattern matching,
node indexes, and relationship traversals.
DOES NOT CALL OR IMPORT RELATIONAL SIMULATOR.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from ..common.fixture_loader import FixtureLoader


class Q08GraphExecutor:
    def __init__(self, fixture: Optional[Dict[str, Any]] = None):
        self.fixture = fixture or FixtureLoader.load_fixture()
        self._build_graph_projection()

    def _build_graph_projection(self):
        """Builds Neo4j in-memory graph projection from fixture."""
        self.nodes_tenant: Dict[int, Dict[str, Any]] = {
            t["id"]: t for t in self.fixture["tenants"]
        }
        self.nodes_user: Dict[int, Dict[str, Any]] = {
            u["id"]: u for u in self.fixture["users"]
        }
        self.nodes_dept: Dict[int, Dict[str, Any]] = {
            d["id"]: d for d in self.fixture["departments"]
        }

        # Build Notice nodes with tenant_id derived during ETL extraction (Pattern R-1)
        self.nodes_notice: Dict[int, Dict[str, Any]] = {}
        for nt in self.fixture["notices"]:
            creator_id = nt["created_by_user_id"]
            # Look up creator's unambiguous tenant in fixture
            creator_mems = [
                m["tenant_id"]
                for m in self.fixture["tenant_user_memberships"]
                if m["user_id"] == creator_id and m["status"] == "active" and not m["is_deleted"]
            ]
            creator_tenant = creator_mems[0] if len(set(creator_mems)) == 1 else None

            self.nodes_notice[nt["id"]] = {
                **nt,
                "tenant_id": creator_tenant
            }

        # Build Audience nodes with tenant_id derived during ETL extraction (Pattern R-4)
        self.nodes_audience: Dict[int, Dict[str, Any]] = {}
        for au in self.fixture["audiences"]:
            if au.get("is_system", False):
                # System audience preserves source tenant_id (must be None to be valid global)
                self.nodes_audience[au["id"]] = {
                    **au,
                    "tenant_id": au.get("tenant_id")
                }
            else:
                # Custom audience ETL validation (Pattern R-4):
                # Verify owner tenant
                owner_id = au.get("owner_user_id")
                owner_mems = [
                    m["tenant_id"]
                    for m in self.fixture["tenant_user_memberships"]
                    if m["user_id"] == owner_id and m["status"] == "active" and not m["is_deleted"]
                ]
                owner_t = owner_mems[0] if len(set(owner_mems)) == 1 else None

                # Verify dept members
                dept_tenants = set()
                dept_valid = True
                for adm in self.fixture["audience_department_members"]:
                    if adm["audience_id"] == au["id"]:
                        d = self.nodes_dept.get(adm["department_id"])
                        if d:
                            dept_tenants.add(d["tenant_id"])
                        else:
                            dept_valid = False

                # Verify user members
                user_tenants = set()
                user_valid = True
                for aum in self.fixture["audience_user_members"]:
                    if aum["audience_id"] == au["id"]:
                        u_mems = [
                            m["tenant_id"]
                            for m in self.fixture["tenant_user_memberships"]
                            if m["user_id"] == aum["user_id"] and m["status"] == "active" and not m["is_deleted"]
                        ]
                        if len(set(u_mems)) == 1:
                            user_tenants.add(u_mems[0])
                        else:
                            user_valid = False

                # If all sources unanimously agree on target tenant -> project with that tenant_id
                # Otherwise, do NOT project with a valid tenant (quarantine / tenant_id=None or unassigned)
                if (owner_t is not None
                    and dept_valid and (not dept_tenants or dept_tenants == {owner_t})
                    and user_valid and (not user_tenants or user_tenants == {owner_t})):
                    self.nodes_audience[au["id"]] = {
                        **au,
                        "tenant_id": owner_t
                    }
                else:
                    # Ambiguous / cross-tenant custom audience is quarantined
                    self.nodes_audience[au["id"]] = {
                        **au,
                        "tenant_id": -1  # Invalid / quarantined
                    }

        # Build Graph Relationships:
        # 1. MEMBER_OF: user_id -> list of edge dicts
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

        # 2. TARGETS_AUDIENCE: notice_id -> audience_id
        self.edges_targets_audience: Dict[int, int] = {
            nt["id"]: nt["audience_id"] for nt in self.fixture["notices"]
        }

        # 3. PUBLISHED_BY: notice_id -> creator user_id
        self.edges_published_by: Dict[int, int] = {
            nt["id"]: nt["created_by_user_id"] for nt in self.fixture["notices"]
        }

        # 4. INCLUDED_IN_AUDIENCE: user_id -> set of audience_ids
        self.edges_included_in_audience: Dict[int, Set[int]] = {}
        for aum in self.fixture["audience_user_members"]:
            uid = aum["user_id"]
            if uid not in self.edges_included_in_audience:
                self.edges_included_in_audience[uid] = set()
            self.edges_included_in_audience[uid].add(aum["audience_id"])

        # 5. DEPARTMENT_IN_AUDIENCE: department_id -> set of audience_ids
        self.edges_dept_in_audience: Dict[int, Set[int]] = {}
        for adm in self.fixture["audience_department_members"]:
            did = adm["department_id"]
            if did not in self.edges_dept_in_audience:
                self.edges_dept_in_audience[did] = set()
            self.edges_dept_in_audience[did].add(adm["audience_id"])

        # 6. MEMBER_OF_DEPARTMENT: user_id -> list of edge dicts
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

    def execute_graph_q08(
        self,
        tenant_id: int,
        requesting_user_id: int,
        notice_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes canonical Q08 Cypher query graph traversal:
        MATCH (t:Tenant {id: $tenant_id, is_deleted: false})
              <-[m:MEMBER_OF {status: 'active', is_deleted: false}]-
              (u:User {id: $requesting_user_id, is_deleted: false, is_active: true})
        MATCH (n:Notice {tenant_id: $tenant_id, is_published: true, is_deleted: false})
              -[:TARGETS_AUDIENCE]->(a:Audience {is_active: true})
        WHERE (a.is_system = true AND a.tenant_id IS NULL AND a.audience_type = 'ALL'
               AND a.owner_user_id IS NULL
               AND NOT EXISTS ((a)<-[:INCLUDED_IN_AUDIENCE]-(:User))
               AND NOT EXISTS ((a)<-[:DEPARTMENT_IN_AUDIENCE]-(:Department)))
           OR (a.is_system = false AND a.tenant_id = $tenant_id
               AND (EXISTS ((u)-[:INCLUDED_IN_AUDIENCE]->(a))
                    OR EXISTS ((u)-[:MEMBER_OF_DEPARTMENT]->(:Department)-[:DEPARTMENT_IN_AUDIENCE]->(a))))
        OPTIONAL MATCH (n)-[:PUBLISHED_BY]->(pub:User)
        RETURN n.id AS notice_id, n.title AS title, ...
        ORDER BY n.published_at DESC, n.id DESC LIMIT 20
        """
        # Pattern 1: MATCH (t:Tenant {id: $tenant_id, is_deleted: false})
        t_node = self.nodes_tenant.get(tenant_id)
        if not t_node or t_node.get("is_deleted", False):
            return []

        # <-[m:MEMBER_OF {status: 'active', is_deleted: false}]-(u:User {id: $requesting_user_id, is_deleted: false, is_active: true})
        u_node = self.nodes_user.get(requesting_user_id)
        if not u_node or not u_node.get("is_active", False) or u_node.get("is_deleted", False):
            return []

        caller_mems = self.edges_member_of.get(requesting_user_id, [])
        is_caller_active = any(
            m["tenant_id"] == tenant_id and m["status"] == "active" and not m["is_deleted"]
            for m in caller_mems
        )
        if not is_caller_active:
            return []

        # Pattern 2: MATCH (n:Notice {tenant_id: $tenant_id, is_published: true, is_deleted: false})-[:TARGETS_AUDIENCE]->(a:Audience {is_active: true})
        matched_records = []
        for n_id, n_node in self.nodes_notice.items():
            if notice_id is not None and n_id != notice_id:
                continue

            if n_node.get("tenant_id") != tenant_id:
                continue
            if not n_node.get("is_published", False) or n_node.get("is_deleted", False):
                continue

            target_aud_id = self.edges_targets_audience.get(n_id)
            if not target_aud_id:
                continue
            a_node = self.nodes_audience.get(target_aud_id)
            if not a_node or not a_node.get("is_active", True):
                continue

            # WHERE Clause: Branch 1 vs Branch 2
            is_authorized = False

            if a_node.get("is_system", False):
                # Branch 1: Global System Audience
                # Graph invariants matching Doc 34:
                # 1. a.is_system = true
                # 2. a.tenant_id IS NULL
                # 3. a.audience_type = 'ALL'
                # 4. a.owner_user_id IS NULL (NOT EXISTS (a)<-[:OWNS_AUDIENCE]-(:User))
                # 5. NOT EXISTS (a)<-[:INCLUDED_IN_AUDIENCE]-(:User)
                # 6. NOT EXISTS (a)<-[:DEPARTMENT_IN_AUDIENCE]-(:Department)
                has_no_tenant = (a_node.get("tenant_id") is None)
                is_type_all = (a_node.get("audience_type") == "ALL")
                has_no_owner = (a_node.get("owner_user_id") is None)

                # Check graph relationship existence:
                has_user_edges = any(
                    target_aud_id in aud_set
                    for aud_set in self.edges_included_in_audience.values()
                )
                has_dept_edges = any(
                    target_aud_id in aud_set
                    for aud_set in self.edges_dept_in_audience.values()
                )

                if (has_no_tenant
                    and is_type_all
                    and has_no_owner
                    and not has_user_edges
                    and not has_dept_edges):
                    is_authorized = True

            else:
                # Branch 2: Custom Tenant Audience
                # Invariants from Cypher:
                # 1. a.is_system = false
                # 2. a.tenant_id = $tenant_id
                # 3. Recipient authorization:
                #    EXISTS { MATCH (u)-[:INCLUDED_IN_AUDIENCE]->(a) }
                #    OR EXISTS { MATCH (u)-[dm:MEMBER_OF_DEPARTMENT {tenant_id: $tenant_id, is_active: true}]->(d:Department {tenant_id: $tenant_id, is_active: true})-[:DEPARTMENT_IN_AUDIENCE]->(a) WHERE dm.effective_to IS NULL }
                if a_node.get("tenant_id") == tenant_id:
                    # Check direct user inclusion
                    is_direct_recipient = target_aud_id in self.edges_included_in_audience.get(requesting_user_id, set())

                    # Check department inclusion
                    is_dept_recipient = False
                    if not is_direct_recipient:
                        user_dm_list = self.edges_member_of_dept.get(requesting_user_id, [])
                        for dm in user_dm_list:
                            if (dm["tenant_id"] == tenant_id
                                and dm["is_active"]
                                and dm["effective_to"] is None):
                                d_node = self.nodes_dept.get(dm["department_id"])
                                if d_node and d_node.get("tenant_id") == tenant_id and d_node.get("is_active", False):
                                    if target_aud_id in self.edges_dept_in_audience.get(dm["department_id"], set()):
                                        is_dept_recipient = True
                                        break

                    if is_direct_recipient or is_dept_recipient:
                        is_authorized = True

            if is_authorized:
                # OPTIONAL MATCH (n)-[:PUBLISHED_BY]->(pub:User)
                pub_id = self.edges_published_by.get(n_id)
                author_name = self._get_display_name(pub_id, tenant_id) if pub_id else "Unknown"

                matched_records.append({
                    "notice_id": n_node["id"],
                    "title": n_node["title"],
                    "notice_type": n_node["notice_type"],
                    "priority": n_node["priority"],
                    "audience_name": a_node["name"],
                    "audience_type": a_node["audience_type"],
                    "is_system_audience": a_node.get("is_system", False),
                    "author_name": author_name,
                    "published_at": n_node["published_at"]
                })

        # ORDER BY n.published_at DESC, n.id DESC LIMIT 20
        matched_records.sort(key=lambda x: (x["published_at"], x["notice_id"]), reverse=True)
        return matched_records[:20]

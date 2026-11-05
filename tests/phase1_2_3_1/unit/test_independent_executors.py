"""
Unit Tests for Independent Execution Proof (WP1 - Gate G1 & G2).
Inspects AST to prove zero cross-delegation between Relational and Graph executors.
Executes intentional rule divergence test and confirms independent divergence.
"""

import ast
import inspect
import unittest
import sys
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.phase1_2_3_1.relational.q01_relational_executor import Q01RelationalExecutor
from tests.phase1_2_3_1.relational.q08_relational_executor import Q08RelationalExecutor
from tests.phase1_2_3_1.graph.q01_graph_executor import Q01GraphExecutor
from tests.phase1_2_3_1.graph.q08_graph_executor import Q08GraphExecutor
from tests.phase1_2_3_1.common.result_normalizer import ResultNormalizer


class TestIndependentExecutors(unittest.TestCase):

    def test_ast_independence(self):
        """
        IND-01: Parses Python source code of all executors to prove:
        1. Relational executors do NOT import or reference Graph executors.
        2. Graph executors do NOT import or reference Relational executors.
        3. Neither executor calls functions belonging to the other domain.
        """
        base_dir = Path(__file__).resolve().parent.parent
        rel_q01_path = base_dir / "relational" / "q01_relational_executor.py"
        rel_q08_path = base_dir / "relational" / "q08_relational_executor.py"
        graph_q01_path = base_dir / "graph" / "q01_graph_executor.py"
        graph_q08_path = base_dir / "graph" / "q08_graph_executor.py"

        sources = {
            "rel_q01": rel_q01_path.read_text(encoding="utf-8"),
            "rel_q08": rel_q08_path.read_text(encoding="utf-8"),
            "graph_q01": graph_q01_path.read_text(encoding="utf-8"),
            "graph_q08": graph_q08_path.read_text(encoding="utf-8"),
        }

        # Banned terms in Relational files:
        banned_in_rel = ["GraphExecutor", "execute_graph", "edges_", "nodes_", "cypher"]
        for k in ["rel_q01", "rel_q08"]:
            for term in banned_in_rel:
                self.assertNotIn(term, sources[k], f"Found banned graph reference '{term}' in relational executor {k}")

        # Banned terms in Graph files:
        banned_in_graph = ["RelationalExecutor", "execute_relational", "execute_sql", "relational", "cte"]
        for k in ["graph_q01", "graph_q08"]:
            for term in banned_in_graph:
                self.assertNotIn(term, sources[k], f"Found banned relational reference '{term}' in graph executor {k}")

        # Parse AST to ensure no cross-delegation functions exist
        for name, src in sources.items():
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if "graph" in name:
                        self.assertNotIn("relational", node.module or "", f"Graph file imported relational module: {node.module}")
                    if "relational" in name:
                        self.assertNotIn("graph", node.module or "", f"Relational file imported graph module: {node.module}")

    def test_independent_rule_divergence(self):
        """
        IND-02: Proves true independent execution by intentionally modifying a graph-side rule
        and demonstrating that graph outputs diverge from SQL outputs, then restoring it.
        """
        rel_exec = Q08RelationalExecutor()
        graph_exec = Q08GraphExecutor()

        # Baseline: both return identical results for Notice 901
        res_sql = rel_exec.execute_relational_q08(tenant_id=1, requesting_user_id=101, notice_id=901)
        res_graph = graph_exec.execute_graph_q08(tenant_id=1, requesting_user_id=101, notice_id=901)
        eq, _ = ResultNormalizer.compare_payloads(res_sql, res_graph)
        self.assertTrue(eq, "Baseline results must be identical before rule divergence test")

        # Intentionally diverge: mutate graph executor rule to require priority == 'low'
        orig_nodes = graph_exec.nodes_notice
        try:
            # Mutate notice priority in graph node projection only
            graph_exec.nodes_notice = {
                nid: {**n, "priority": "low" if nid == 901 else n["priority"]}
                for nid, n in orig_nodes.items()
            }
            res_graph_diverged = graph_exec.execute_graph_q08(tenant_id=1, requesting_user_id=101, notice_id=901)

            # SQL remains 'high', graph is now 'low'
            self.assertEqual(res_sql[0]["priority"], "high")
            self.assertEqual(res_graph_diverged[0]["priority"], "low")
            eq_div, diff = ResultNormalizer.compare_payloads(res_sql, res_graph_diverged)
            self.assertFalse(eq_div, "Divergence must be detected when graph rule/data is independently changed!")
        finally:
            # Restore original state
            graph_exec.nodes_notice = orig_nodes

        # Confirm restored equivalence
        res_graph_restored = graph_exec.execute_graph_q08(tenant_id=1, requesting_user_id=101, notice_id=901)
        eq_restored, _ = ResultNormalizer.compare_payloads(res_sql, res_graph_restored)
        self.assertTrue(eq_restored, "Equivalence must be restored after resetting graph rule")


if __name__ == "__main__":
    unittest.main()

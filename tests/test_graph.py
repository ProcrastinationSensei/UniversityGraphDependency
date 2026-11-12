import json
import os
import tempfile
import unittest

from src.graph import build_graph_dfs, compute_load_order


class TestGraph(unittest.TestCase):

    def __init__(self, method_name: str = "runTest") -> None:
        super().__init__(method_name)
        self.data = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
            "CYCLE_1": ["CYCLE_2"],
            "CYCLE_2": ["CYCLE_1"],
            "TEST_X": ["X_FILTER"],
            "X_FILTER": [],
        }
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".json"
        ) as tmp_file:
            json.dump(self.data, tmp_file)
            self.repo_file = tmp_file.name
        self.addCleanup(os.remove, self.repo_file)

    def test_dfs_graph_building(self) -> None:
        graph = build_graph_dfs(
            "A", self.repo_file, test_mode=True, max_depth=5, filter_sub=""
        )
        self.assertIn("A", graph.adj)
        self.assertIn("B", graph.adj["A"])
        self.assertIn("C", graph.adj["A"])
        self.assertIn("D", graph.adj["B"])

    def test_depth_limiting(self) -> None:
        graph = build_graph_dfs(
            "A", self.repo_file, test_mode=True, max_depth=1, filter_sub=""
        )
        self.assertIn("A", graph.adj)
        self.assertEqual(graph.adj.get("B", []), [])

    def test_filter_substring(self) -> None:
        graph = build_graph_dfs(
            "TEST_X",
            self.repo_file,
            test_mode=True,
            max_depth=3,
            filter_sub="X",
        )
        self.assertEqual(graph.adj, {})

    def test_cycle_detection(self) -> None:
        graph = build_graph_dfs(
            "CYCLE_1",
            self.repo_file,
            test_mode=True,
            max_depth=5,
            filter_sub="",
        )
        self.assertTrue(len(graph.cycles) > 0)

    def test_load_order(self) -> None:
        graph = build_graph_dfs(
            "A", self.repo_file, test_mode=True, max_depth=5, filter_sub=""
        )
        order = compute_load_order(graph, "A")
        self.assertEqual(order[-1], "A")
        self.assertIn("D", order)


if __name__ == "__main__":
    unittest.main()

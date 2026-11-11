"""Unit tests for dependency graph algorithm and operations."""

import json
import os
import tempfile
import unittest

from src.graph import build_graph_dfs, compute_load_order


class TestGraph(unittest.TestCase):
    """Test suite for graph construction and load order."""

    def setUp(self) -> None:
        """Create sample repository graph file."""
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
        self.tmp_file = tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".json"
        )
        json.dump(self.data, self.tmp_file)
        self.tmp_file.close()

    def tearDown(self) -> None:
        """Clean up temporary test file."""
        os.remove(self.tmp_file.name)

    def test_dfs_graph_building(self) -> None:
        """Test building dependency graph using non-recursive DFS."""
        graph = build_graph_dfs(
            "A", self.tmp_file.name, test_mode=True, max_depth=5, filter_sub=""
        )
        self.assertIn("A", graph.adj)
        self.assertIn("B", graph.adj["A"])
        self.assertIn("C", graph.adj["A"])
        self.assertIn("D", graph.adj["B"])

    def test_depth_limiting(self) -> None:
        """Test max_depth parameter stops exploration."""
        graph = build_graph_dfs(
            "A", self.tmp_file.name, test_mode=True, max_depth=1, filter_sub=""
        )
        self.assertIn("A", graph.adj)
        # Depth 1 allows direct children B, C but not exploring B's child D
        self.assertEqual(graph.adj.get("B", []), [])

    def test_filter_substring(self) -> None:
        """Test filter_substring ignores matching packages."""
        graph = build_graph_dfs(
            "TEST_X",
            self.tmp_file.name,
            test_mode=True,
            max_depth=3,
            filter_sub="X",
        )
        self.assertEqual(graph.adj, {})

    def test_cycle_detection(self) -> None:
        """Test cycle detection in graph."""
        graph = build_graph_dfs(
            "CYCLE_1",
            self.tmp_file.name,
            test_mode=True,
            max_depth=5,
            filter_sub="",
        )
        self.assertTrue(len(graph.cycles) > 0)

    def test_load_order(self) -> None:
        """Test post-order dependency load order calculation."""
        graph = build_graph_dfs(
            "A", self.tmp_file.name, test_mode=True, max_depth=5, filter_sub=""
        )
        order = compute_load_order(graph, "A")
        self.assertEqual(order[-1], "A")
        self.assertIn("D", order)


if __name__ == "__main__":
    unittest.main()

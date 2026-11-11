"""Unit tests for D2 and SVG visualization generator."""

import os
import tempfile
import unittest

from src.graph import DependencyGraph
from src.visualizer import generate_d2_code, generate_svg_image


class TestVisualizer(unittest.TestCase):
    """Test suite for diagram visualization outputs."""

    def setUp(self) -> None:
        """Set up simple graph for visualization tests."""
        self.graph = DependencyGraph()
        self.graph.add_edge("A", "B")
        self.graph.add_edge("A", "C")
        self.graph.add_edge("B", "D")

    def test_generate_d2_code(self) -> None:
        """Test generating D2 diagram text."""
        d2 = generate_d2_code(self.graph)
        self.assertIn('"A" -> "B"', d2)
        self.assertIn('"A" -> "C"', d2)
        self.assertIn('"B" -> "D"', d2)

    def test_generate_svg_image(self) -> None:
        """Test rendering SVG image file."""
        tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".svg")
        tmp.close()
        try:
            generate_svg_image(self.graph, tmp.name, "A")
            self.assertTrue(os.path.exists(tmp.name))
            with open(tmp.name, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("<svg", content)
            self.assertIn("Dependency Graph: A", content)
        finally:
            os.remove(tmp.name)


if __name__ == "__main__":
    unittest.main()

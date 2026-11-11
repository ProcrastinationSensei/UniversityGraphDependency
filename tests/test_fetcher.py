"""Unit tests for fetcher module."""

import json
import os
import tempfile
import unittest

from src.fetcher import fetch_direct_dependencies


class TestFetcher(unittest.TestCase):
    """Test suite for data fetcher."""

    def test_fetch_from_test_repo(self) -> None:
        """Test fetching dependencies from local test JSON repository."""
        data = {"A": ["B", "C"], "B": ["D"]}
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            tmp_name = f.name

        try:
            deps_a = fetch_direct_dependencies("A", tmp_name, test_mode=True)
            self.assertEqual(deps_a, ["B", "C"])

            deps_b = fetch_direct_dependencies("B", tmp_name, test_mode=True)
            self.assertEqual(deps_b, ["D"])

            deps_none = fetch_direct_dependencies(
                "NON_EXISTENT", tmp_name, test_mode=True
            )
            self.assertEqual(deps_none, [])
        finally:
            os.remove(tmp_name)


if __name__ == "__main__":
    unittest.main()

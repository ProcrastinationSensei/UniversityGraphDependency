import os
import tempfile
import unittest

from src.config import Config, load_config, validate_config


class TestConfig(unittest.TestCase):

    def test_valid_config(self) -> None:
        cfg = Config("express", "http://example.com", False, "out.svg", 3, "")
        validate_config(cfg)

    def test_empty_package_name_raises(self) -> None:
        cfg = Config("", "http://example.com", False, "out.svg", 3, "")
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_negative_depth_raises(self) -> None:
        cfg = Config("express", "http://example.com", False, "out.svg", -1, "")
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_load_config_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_config("non_existent_file.toml")

    def test_load_config_from_file(self) -> None:
        content = (
            'package_name = "react"\n'
            'repo_url = "https://registry.npmjs.org"\n'
            "test_mode = false\n"
            'output_file = "react.svg"\n'
            "max_depth = 2\n"
            'filter_substring = ""\n'
        )
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".toml"
        ) as f:
            f.write(content)
            tmp_name = f.name

        try:
            cfg = load_config(tmp_name)
            self.assertEqual(cfg.package_name, "react")
            self.assertEqual(cfg.max_depth, 2)
            self.assertFalse(cfg.test_mode)
        finally:
            os.remove(tmp_name)


if __name__ == "__main__":
    unittest.main()

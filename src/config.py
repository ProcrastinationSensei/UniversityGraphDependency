"""Configuration module for Dependency Visualizer.

Parses and validates user configuration from TOML files.
"""

from dataclasses import dataclass
import os
import sys

# Constants to avoid magic numbers
MIN_DEPTH_LIMIT = 0
MAX_DEPTH_UPPER_BOUND = 100


@dataclass
class Config:
    """Dataclass holding all configuration parameters."""

    package_name: str
    repo_url: str
    test_mode: bool
    output_file: str
    max_depth: int
    filter_substring: str


def load_config(file_path: str) -> Config:
    """Load configuration from a TOML file.

    Raises FileNotFoundError if file does not exist or ValueError on parse.
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Config file '{file_path}' not found.")

    try:
        if sys.version_info >= (3, 11):
            import tomllib

            with open(file_path, "rb") as fp:
                data = tomllib.load(fp)
        else:
            data = _parse_simple_toml(file_path)
    except Exception as exc:
        raise ValueError(f"Failed to parse TOML configuration: {exc}")

    config = Config(
        package_name=str(data.get("package_name", "")).strip(),
        repo_url=str(data.get("repo_url", "")).strip(),
        test_mode=bool(data.get("test_mode", False)),
        output_file=str(data.get("output_file", "graph.svg")).strip(),
        max_depth=int(data.get("max_depth", MIN_DEPTH_LIMIT)),
        filter_substring=str(data.get("filter_substring", "")),
    )
    validate_config(config)
    return config


def _parse_simple_toml(file_path: str) -> dict:
    """Fallback simple TOML line parser for legacy python environments."""
    result = {}
    with open(file_path, "r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val.lower() == "true":
                    result[key] = True
                elif val.lower() == "false":
                    result[key] = False
                elif val.isdigit():
                    result[key] = int(val)
                else:
                    result[key] = val
    return result


def validate_config(config: Config) -> None:
    """Validate parameter values in configuration object.

    Raises ValueError if any parameter is invalid.
    """

    if not config.package_name:
        raise ValueError("Config error: 'package_name' must not be empty.")

    if not config.repo_url:
        raise ValueError("Config error: 'repo_url' must not be empty.")

    if config.max_depth < MIN_DEPTH_LIMIT:
        raise ValueError("Config error: 'max_depth' cannot be negative.")

    if config.max_depth > MAX_DEPTH_UPPER_BOUND:
        raise ValueError(
            f"Config error: 'max_depth' exceeds max limit "
            f"({MAX_DEPTH_UPPER_BOUND})."
        )


def print_config(config: Config) -> None:
    """Print configuration parameters in key-value format for Stage 1."""

    print("=== Configuration Parameters ===")
    print(f"package_name: {config.package_name}")
    print(f"repo_url: {config.repo_url}")
    print(f"test_mode: {config.test_mode}")
    print(f"output_file: {config.output_file}")
    print(f"max_depth: {config.max_depth}")
    print(f"filter_substring: {config.filter_substring}")
    print("================================")

"""Data fetching module for npm registry and test repository.

Extracts direct package dependencies using standard urllib or local files.
"""

import json
import os
import urllib.error
import urllib.request

HTTP_OK = 200
DEFAULT_TIMEOUT_SEC = 5


def fetch_direct_dependencies(
    package_name: str, repo_url: str, test_mode: bool
) -> list[str]:
    """Fetch direct dependencies for a package.

    Routes to local JSON test repository if test_mode is True,
    or npm registry HTTP API if test_mode is False.
    """

    if test_mode:
        return _fetch_from_test_repo(package_name, repo_url)
    return _fetch_from_npm_registry(package_name, repo_url)


def _fetch_from_test_repo(package_name: str, repo_file: str) -> list[str]:
    """Fetch direct dependencies from local test graph JSON file."""

    if not os.path.isfile(repo_file):
        raise FileNotFoundError(
            f"Test repository file '{repo_file}' not found."
        )

    with open(repo_file, "r", encoding="utf-8") as fp:
        graph_data = json.load(fp)

    if package_name not in graph_data:
        return []

    deps = graph_data.get(package_name, [])
    if isinstance(deps, list):
        return [str(item) for item in deps]
    return []


def _fetch_from_npm_registry(package_name: str, repo_url: str) -> list[str]:
    """Fetch direct dependencies from npm registry endpoint."""

    base_url = repo_url.rstrip("/")
    # Fetch package latest version metadata
    target_url = f"{base_url}/{package_name}/latest"
    req = urllib.request.Request(
        target_url, headers={"User-Agent": "DependencyVisualizer/1.0"}
    )

    try:
        with urllib.request.urlopen(
            req, timeout=DEFAULT_TIMEOUT_SEC
        ) as response:
            if response.status != HTTP_OK:
                raise ValueError(
                    f"HTTP error {response.status} fetching '{package_name}'"
                )
            content = response.read().decode("utf-8")
            metadata = json.loads(content)
            deps_dict = metadata.get("dependencies", {})
            return list(deps_dict.keys())
    except urllib.error.HTTPError as err:
        if err.code == 404:
            # Package not found or has no dependencies
            return []
        raise ValueError(
            f"Failed to fetch package '{package_name}': HTTP {err.code}"
        )
    except urllib.error.URLError as err:
        raise ValueError(
            f"Network connection error fetching '{package_name}': {err.reason}"
        )
    except Exception as err:
        raise ValueError(
            f"Error processing npm metadata for '{package_name}': {err}"
        )

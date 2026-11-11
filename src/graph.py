"""Dependency graph construction and operations module.

Builds dependency graph using non-recursive DFS and computes load order.
"""

from src.fetcher import fetch_direct_dependencies

INITIAL_DEPTH = 0


class DependencyGraph:
    """Class representing dependency graph and detected cycles."""

    def __init__(self) -> None:
        """Initialize empty graph dictionary and cycle list."""
        self.adj: dict[str, list[str]] = {}
        self.cycles: list[str] = []

    def add_edge(self, parent: str, child: str) -> None:
        """Add directed edge from parent package to child package."""
        if parent not in self.adj:
            self.adj[parent] = []
        if child not in self.adj[parent]:
            self.adj[parent].append(child)

    def ensure_node(self, node: str) -> None:
        """Ensure node exists in adjacency dictionary."""
        if node not in self.adj:
            self.adj[node] = []


def build_graph_dfs(
    start_pkg: str,
    repo_url: str,
    test_mode: bool,
    max_depth: int,
    filter_sub: str,
) -> DependencyGraph:
    """Build dependency graph using iterative DFS without recursion."""

    graph = DependencyGraph()
    if filter_sub and filter_sub in start_pkg:
        return graph

    graph.ensure_node(start_pkg)
    stack: list[tuple[str, int, tuple[str, ...]]] = [
        (start_pkg, INITIAL_DEPTH, (start_pkg,))
    ]
    visited: set[str] = set()

    while stack:
        node, depth, path = stack.pop()
        graph.ensure_node(node)

        if node in visited or depth >= max_depth:
            continue
        visited.add(node)

        deps = fetch_direct_dependencies(node, repo_url, test_mode)
        _process_node_deps(graph, stack, node, depth, path, deps, filter_sub)

    return graph


def _process_node_deps(
    graph: DependencyGraph,
    stack: list,
    node: str,
    depth: int,
    path: tuple[str, ...],
    deps: list[str],
    filter_sub: str,
) -> None:
    """Process child dependencies for a single node in DFS traversal."""
    for dep in deps:
        if filter_sub and filter_sub in dep:
            continue

        graph.add_edge(node, dep)

        if dep in path:
            cycle_repr = " -> ".join(path) + f" -> {dep}"
            if cycle_repr not in graph.cycles:
                graph.cycles.append(cycle_repr)
        else:
            stack.append((dep, depth + 1, path + (dep,)))


def compute_load_order(graph: DependencyGraph, start_pkg: str) -> list[str]:
    """Compute dependency load order using non-recursive post-order DFS."""

    load_order: list[str] = []
    visited: set[str] = set()

    if start_pkg not in graph.adj and not graph.adj:
        return load_order

    stack: list[list] = [[start_pkg, 0]]
    in_path: set[str] = {start_pkg}

    while stack:
        node, idx = stack[-1]
        children = graph.adj.get(node, [])

        if idx < len(children):
            stack[-1][1] += 1
            child = children[idx]
            if child not in visited and child not in in_path:
                in_path.add(child)
                stack.append([child, 0])
        else:
            stack.pop()
            in_path.discard(node)
            if node not in visited:
                visited.add(node)
                load_order.append(node)

    return load_order

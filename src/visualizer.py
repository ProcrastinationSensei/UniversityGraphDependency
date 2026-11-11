"""Visualization module for D2 markup and SVG diagram generation.

Generates D2 diagram text and renders pure SVG vector graphics diagrams.
"""

from src.graph import DependencyGraph

# Layout constants for SVG generation
BOX_WIDTH = 130
BOX_HEIGHT = 40
X_GAP = 180
Y_GAP = 70
MARGIN_X = 50
MARGIN_Y = 80


def generate_d2_code(graph: DependencyGraph) -> str:
    """Generate D2 diagram language description of dependency graph."""

    lines = ["# D2 Dependency Graph Visualization"]
    visited_edges: set[tuple[str, str]] = set()

    for parent, children in graph.adj.items():
        if not children:
            lines.append(f'"{parent}"')
            continue
        for child in children:
            edge = (parent, child)
            if edge not in visited_edges:
                visited_edges.add(edge)
                lines.append(f'"{parent}" -> "{child}"')

    return "\n".join(lines)


def generate_svg_image(
    graph: DependencyGraph, output_file: str, root_pkg: str = ""
) -> None:
    """Generate SVG image file representing dependency graph."""

    ranks = _compute_node_ranks(graph, root_pkg)
    positions = _calculate_positions(ranks)
    width, height = _calculate_canvas_size(positions)

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "  .node { font-family: monospace; font-size: 13px; fill: #ffffff; }",
        "  .title { font-family: sans-serif; font-size: 16px; "
        "font-weight: bold; fill: #1e293b; }",
        "  .edge { stroke: #64748b; stroke-width: 2; fill: none; }",
        "</style>",
        "<defs>",
        '  <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '    <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/>',
        "  </marker>",
        "</defs>",
        f'<text x="{MARGIN_X}" y="40" class="title">'
        f"Dependency Graph: {root_pkg}</text>",
    ]

    # Draw edges
    svg_parts.extend(_draw_svg_edges(graph, positions))

    # Draw nodes
    svg_parts.extend(_draw_svg_nodes(positions, root_pkg))

    svg_parts.append("</svg>")

    with open(output_file, "w", encoding="utf-8") as fp:
        fp.write("\n".join(svg_parts))


def _compute_node_ranks(
    graph: DependencyGraph, root_pkg: str
) -> dict[int, list[str]]:
    """Assign graph nodes to horizontal layout ranks based on BFS depth."""

    ranks: dict[int, list[str]] = {}
    node_rank: dict[str, int] = {}

    if not graph.adj:
        return ranks

    start_node = (
        root_pkg if root_pkg in graph.adj else next(iter(graph.adj.keys()))
    )
    queue = [(start_node, 0)]
    visited = {start_node}

    while queue:
        node, depth = queue.pop(0)
        node_rank[node] = depth
        ranks.setdefault(depth, [])
        if node not in ranks[depth]:
            ranks[depth].append(node)

        for child in graph.adj.get(node, []):
            if child not in visited:
                visited.add(child)
                queue.append((child, depth + 1))

    # Catch orphan nodes
    for node in graph.adj:
        if node not in node_rank:
            max_r = max(ranks.keys()) if ranks else 0
            ranks.setdefault(max_r, []).append(node)

    return ranks


def _calculate_positions(
    ranks: dict[int, list[str]]
) -> dict[str, tuple[int, int]]:
    """Calculate X, Y canvas coordinates for each node."""

    positions = {}
    for rank_idx, nodes in ranks.items():
        x = MARGIN_X + rank_idx * X_GAP
        for node_idx, node in enumerate(nodes):
            y = MARGIN_Y + node_idx * Y_GAP
            positions[node] = (x, y)
    return positions


def _calculate_canvas_size(
    positions: dict[str, tuple[int, int]]
) -> tuple[int, int]:
    """Calculate SVG canvas width and height based on node coordinates."""

    if not positions:
        return (400, 300)
    max_x = max(x for x, _ in positions.values()) + BOX_WIDTH + MARGIN_X
    max_y = max(y for _, y in positions.values()) + BOX_HEIGHT + MARGIN_Y
    return (max(max_x, 500), max(max_y, 300))


def _draw_svg_edges(
    graph: DependencyGraph, positions: dict[str, tuple[int, int]]
) -> list[str]:
    """Generate SVG XML elements for directed edges between nodes."""

    edge_elements = []
    for parent, children in graph.adj.items():
        if parent not in positions:
            continue
        px, py = positions[parent]
        p_cx = px + BOX_WIDTH
        p_cy = py + BOX_HEIGHT // 2

        for child in children:
            if child not in positions:
                continue
            cx, cy = positions[child]
            c_cx = cx
            c_cy = cy + BOX_HEIGHT // 2

            path_d = (
                f"M {p_cx} {p_cy} C {p_cx + 40} {p_cy}, "
                f"{c_cx - 40} {c_cy}, {c_cx} {c_cy}"
            )
            edge_elements.append(
                f'<path d="{path_d}" class="edge" marker-end="url(#arrow)"/>'
            )
    return edge_elements


def _draw_svg_nodes(
    positions: dict[str, tuple[int, int]], root_pkg: str
) -> list[str]:
    """Generate SVG XML elements for graph nodes with custom styling."""

    node_elements = []
    for node, (x, y) in positions.items():
        color = "#2563eb" if node == root_pkg else "#475569"
        node_elements.append(
            f'<rect x="{x}" y="{y}" width="{BOX_WIDTH}" '
            f'height="{BOX_HEIGHT}" rx="6" fill="{color}"/>'
        )
        tx = x + 10
        ty = y + 24
        # Truncate label if too long
        display_name = node[:14] + ".." if len(node) > 16 else node
        node_elements.append(
            f'<text x="{tx}" y="{ty}" class="node">{display_name}</text>'
        )
    return node_elements

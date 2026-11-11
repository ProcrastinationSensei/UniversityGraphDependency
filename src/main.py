"""Main CLI entry point for Dependency Visualizer (Variant 16).

Executes stages 1 to 5 of dependency analysis and graph visualization.
"""

import argparse
import sys

from src.config import Config, load_config, print_config
from src.fetcher import fetch_direct_dependencies
from src.graph import build_graph_dfs, compute_load_order
from src.visualizer import generate_d2_code, generate_svg_image


def parse_cli_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Dependency Visualizer (Variant 16) - npm / test mode"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.toml",
        help="Path to TOML configuration file",
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Execute specific stage (1-5)",
    )
    return parser.parse_args()


def run_stage_1(config: Config) -> None:
    """Stage 1: Output all user-configured parameters in key-value format."""
    print("\n--- STAGE 1: Minimal Prototype & Configuration ---")
    print_config(config)


def run_stage_2(config: Config) -> None:
    """Stage 2: Fetch and display direct dependencies."""
    print("\n--- STAGE 2: Data Collection (Direct Dependencies) ---")
    try:
        deps = fetch_direct_dependencies(
            config.package_name, config.repo_url, config.test_mode
        )
        print(f"Direct dependencies for '{config.package_name}':")
        if not deps:
            print("  (No direct dependencies found)")
        for dep in deps:
            print(f"  - {dep}")
    except Exception as err:
        print(f"Stage 2 Error: {err}")


def run_stage_3(config: Config):
    """Stage 3: Build dependency graph using non-recursive DFS."""
    print("\n--- STAGE 3: Main Operations (DFS Graph Construction) ---")
    graph = build_graph_dfs(
        config.package_name,
        config.repo_url,
        config.test_mode,
        config.max_depth,
        config.filter_substring,
    )
    print(f"Built graph with {len(graph.adj)} nodes:")
    for parent, children in graph.adj.items():
        children_str = ", ".join(children) if children else "None"
        print(f"  {parent} -> [{children_str}]")

    if graph.cycles:
        print("\nDetected Cyclic Dependencies:")
        for cycle in graph.cycles:
            print(f"  [CYCLE WARNING] {cycle}")
    else:
        print("No cyclic dependencies detected.")
    return graph


def run_stage_4(config: Config, graph) -> None:
    """Stage 4: Compute and output dependency load order."""
    print("\n--- STAGE 4: Additional Operations (Load Order) ---")
    load_order = compute_load_order(graph, config.package_name)
    print(f"Installation / Load Order for '{config.package_name}':")
    for idx, pkg in enumerate(load_order, start=1):
        print(f"  {idx}. {pkg}")

    print("\n=== Comparison with Real Package Manager (npm) ===")
    print(
        "1. Real npm installs dependencies using tree hoisting and "
        "flattening (node_modules structure)."
    )
    print(
        "2. npm resolves version constraints (semver ranges) and deduplicates "
        "shared packages."
    )
    print(
        "3. Our tool computes post-order DFS load sequence, ensuring "
        "leaf dependencies are evaluated before parent packages."
    )


def run_stage_5(config: Config, graph) -> None:
    """Stage 5: Generate D2 markup and SVG diagram."""
    print("\n--- STAGE 5: Visualization (D2 & SVG) ---")
    d2_code = generate_d2_code(graph)
    print("Generated D2 Diagram Code:")
    print("--------------------------------")
    print(d2_code)
    print("--------------------------------")

    d2_filename = config.output_file.replace(".svg", ".d2")
    with open(d2_filename, "w", encoding="utf-8") as fp:
        fp.write(d2_code)
    print(f"Saved D2 markup to: {d2_filename}")

    generate_svg_image(graph, config.output_file, config.package_name)
    print(f"Saved SVG visualization to: {config.output_file}")


def main() -> None:
    """Main application execution pipeline."""
    args = parse_cli_args()
    try:
        config = load_config(args.config)
    except Exception as err:
        print(f"Configuration Loading Error: {err}", file=sys.stderr)
        sys.exit(1)

    target_stage = args.stage

    if target_stage is None or target_stage == 1:
        run_stage_1(config)

    if target_stage is None or target_stage == 2:
        run_stage_2(config)

    if target_stage is None or target_stage >= 3:
        graph = run_stage_3(config)

        if target_stage is None or target_stage == 4:
            run_stage_4(config, graph)

        if target_stage is None or target_stage == 5:
            run_stage_5(config, graph)


if __name__ == "__main__":
    main()

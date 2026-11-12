import argparse
import sys
from typing import Optional

from src.config import Config, load_config, print_config
from src.fetcher import fetch_direct_dependencies
from src.graph import DependencyGraph, build_graph_dfs, compute_load_order
from src.visualizer import generate_d2_code, generate_svg_image

STAGE_CONFIGURATION = 1
STAGE_DIRECT_DEPENDENCIES = 2
STAGE_GRAPH_CONSTRUCTION = 3
STAGE_LOAD_ORDER = 4
STAGE_VISUALIZATION = 5
SUPPORTED_STAGES = (
    STAGE_CONFIGURATION,
    STAGE_DIRECT_DEPENDENCIES,
    STAGE_GRAPH_CONSTRUCTION,
    STAGE_LOAD_ORDER,
    STAGE_VISUALIZATION,
)


def parse_cli_args() -> argparse.Namespace:
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
        choices=SUPPORTED_STAGES,
        help="Execute specific stage (1-5)",
    )
    return parser.parse_args()


def run_stage_1(config: Config) -> None:
    print("\n--- STAGE 1: Minimal Prototype & Configuration ---")
    print_config(config)


def run_stage_2(config: Config) -> None:
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


def run_stage_3(config: Config) -> DependencyGraph:
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


def run_stage_4(config: Config, graph: DependencyGraph) -> None:
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


def run_stage_5(config: Config, graph: DependencyGraph) -> None:
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


def _run_requested_stages(
    config: Config, target_stage: Optional[int]
) -> None:
    if target_stage is None:
        run_stage_1(config)
        run_stage_2(config)
        graph = run_stage_3(config)
        run_stage_4(config, graph)
        run_stage_5(config, graph)
        return

    if target_stage == STAGE_CONFIGURATION:
        run_stage_1(config)
    elif target_stage == STAGE_DIRECT_DEPENDENCIES:
        run_stage_2(config)
    else:
        graph = run_stage_3(config)
        if target_stage == STAGE_LOAD_ORDER:
            run_stage_4(config, graph)
        elif target_stage == STAGE_VISUALIZATION:
            run_stage_5(config, graph)


def main() -> None:
    args = parse_cli_args()
    try:
        config = load_config(args.config)
    except Exception as err:
        print(f"Configuration Loading Error: {err}", file=sys.stderr)
        sys.exit(1)

    _run_requested_stages(config, args.stage)


if __name__ == "__main__":
    main()

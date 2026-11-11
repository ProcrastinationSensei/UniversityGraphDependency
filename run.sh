#!/usr/bin/env bash
set -e

echo "=== Running Unit Tests ==="
python3 -m unittest discover -s tests

echo ""
echo "=== Running Dependency Visualizer (Test Mode Demo) ==="
python3 -m src.main --config test_config.toml

echo ""
echo "=== Execution Complete ==="

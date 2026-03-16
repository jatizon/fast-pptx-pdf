#!/usr/bin/env bash
# Pre-publish validation: tests, build, twine check.
# Run from repository root. Exits non-zero on first failure.
set -e
cd "$(dirname "$0")/.."

echo "=== Running tests ==="
python -m pytest -v --tb=short

echo "=== Building package ==="
pip install build -q
python -m build

echo "=== Checking dist with twine ==="
pip install twine -q
python -m twine check dist/*

echo "=== Pre-publish checks passed ==="

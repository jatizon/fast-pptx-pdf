# Pre-publish validation: tests, build, twine check.
# Run from repository root. Exits non-zero on first failure.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== Running tests ==="
python -m pytest -v --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "=== Building package ==="
pip install build -q
python -m build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "=== Checking dist with twine ==="
pip install twine -q
python -m twine check dist/*
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "=== Pre-publish checks passed ==="

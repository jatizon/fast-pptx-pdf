"""Pytest fixtures."""

import os
from pathlib import Path

import pytest


@pytest.fixture
def sample_pptx_path(tmp_path: Path) -> Path:
    """Create a minimal .pptx file (PPTX is a ZIP); for tests that need a file to exist."""
    # Minimal valid PPTX is a zip with [Content_Types].xml and ppt/ folder. For unit tests
    # we only need a file with .pptx extension that exists; converter will be mocked.
    p = tmp_path / "sample.pptx"
    p.write_bytes(b"PK\x03\x04")  # ZIP magic; enough for path checks
    return p


@pytest.fixture
def env_no_libreoffice(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove FAST_PPTX_PDF_LIBREOFFICE and ensure which('soffice') fails."""
    monkeypatch.delenv("FAST_PPTX_PDF_LIBREOFFICE", raising=False)
    # We cannot easily make shutil.which return None for soffice without patching
    # (platform-dependent). Tests that need "LO not found" can set a bad path override.

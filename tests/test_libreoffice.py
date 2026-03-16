"""Tests for libreoffice.find_libreoffice."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from fast_pptx_pdf.libreoffice import find_libreoffice
from fast_pptx_pdf.exceptions import LibreOfficeNotFoundError


def test_find_libreoffice_override_file(tmp_path: Path) -> None:
    soffice = tmp_path / "soffice.exe"
    soffice.touch()
    assert find_libreoffice(str(soffice)) == str(soffice.resolve())


def test_find_libreoffice_override_dir(tmp_path: Path) -> None:
    (tmp_path / "soffice.exe").touch()
    assert find_libreoffice(str(tmp_path)) == str((tmp_path / "soffice.exe").resolve())


def test_find_libreoffice_override_invalid_raises() -> None:
    with pytest.raises(LibreOfficeNotFoundError) as exc_info:
        find_libreoffice("/nonexistent/path/soffice")
    assert "override" in str(exc_info.value).lower()


def test_find_libreoffice_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    soffice = tmp_path / "soffice"
    soffice.touch()
    monkeypatch.setenv("FAST_PPTX_PDF_LIBREOFFICE", str(soffice))
    with patch("shutil.which", return_value=None):
        with patch("glob.glob", return_value=[]):
            assert find_libreoffice(None) == str(soffice.resolve())


def test_find_libreoffice_from_path() -> None:
    with patch("shutil.which") as which:
        which.return_value = "/usr/bin/soffice"
        with patch("os.name", "posix"):
            with patch("glob.glob", return_value=[]):
                assert find_libreoffice(None) == "/usr/bin/soffice"


def test_find_libreoffice_not_found_raises() -> None:
    with patch("shutil.which", return_value=None):
        with patch("glob.glob", return_value=[]):
            with patch("os.path.isfile", return_value=False):
                with patch("os.name", "posix"):
                    with pytest.raises(LibreOfficeNotFoundError):
                        find_libreoffice(None)

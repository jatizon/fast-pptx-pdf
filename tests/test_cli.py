"""Tests for CLI."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from fast_pptx_pdf.cli import main


def test_cli_file_prints_output_path(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    (tmp_path / "x.pptx").write_bytes(b"PK")
    (tmp_path / "x.pdf").touch()

    with patch("fast_pptx_pdf.cli.convert_file") as cf:
        cf.return_value = tmp_path / "x.pdf"
        sys.argv = ["fast-pptx-pdf", str(tmp_path / "x.pptx")]
        main()
    out, _ = capsys.readouterr()
    assert "x.pdf" in out or str(tmp_path / "x.pdf") in out


def test_cli_nonexistent_path_exits_nonzero() -> None:
    with patch("sys.exit") as exit_mock:
        sys.argv = ["fast-pptx-pdf", "/nonexistent/path.pptx"]
        main()
        exit_mock.assert_called_once_with(1)


def test_cli_wrong_extension_exits_nonzero(tmp_path: Path) -> None:
    (tmp_path / "x.doc").touch()
    with patch("sys.exit") as exit_mock:
        sys.argv = ["fast-pptx-pdf", str(tmp_path / "x.doc")]
        main()
        exit_mock.assert_called_with(1)
        assert exit_mock.call_count >= 1


def test_cli_help(capsys: pytest.CaptureFixture) -> None:
    sys.argv = ["fast-pptx-pdf", "--help"]
    try:
        main()
    except SystemExit:
        pass
    out, _ = capsys.readouterr()
    assert "Convert PPTX" in out
    assert "--workers" in out

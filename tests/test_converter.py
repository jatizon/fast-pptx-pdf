"""Tests for converter.convert_one."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from fast_pptx_pdf.converter import convert_one


def test_convert_one_not_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        convert_one(tmp_path / "missing.pptx", profile_url="file:///tmp/p")


def test_convert_one_wrong_extension_raises(tmp_path: Path) -> None:
    (tmp_path / "doc.doc").touch()
    with pytest.raises(ValueError):
        convert_one(tmp_path / "doc.doc", profile_url="file:///tmp/p")


def test_convert_one_success(tmp_path: Path, sample_pptx_path: Path) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    pdf_path = out_dir / (sample_pptx_path.stem + ".pdf")
    pdf_path.touch()

    with patch("fast_pptx_pdf.converter.find_libreoffice", return_value="/usr/bin/soffice"):
        with patch("fast_pptx_pdf.converter.run_soffice"):
            result = convert_one(
                sample_pptx_path,
                output_dir=out_dir,
                profile_url="file:///tmp/profile",
            )
    assert result == pdf_path


def test_convert_one_calls_soffice_with_profile(tmp_path: Path, sample_pptx_path: Path) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / (sample_pptx_path.stem + ".pdf")).touch()

    with patch("fast_pptx_pdf.converter.find_libreoffice", return_value="/usr/bin/soffice"):
        with patch("fast_pptx_pdf.converter.run_soffice") as run:
            convert_one(
                sample_pptx_path,
                output_dir=out_dir,
                profile_url="file:///tmp/profile_x",
            )
            call_cmd = run.call_args[0][0]
            assert "-env:UserInstallation=file:///tmp/profile_x" in call_cmd
            assert "--headless" in call_cmd
            assert "--convert-to" in call_cmd
            assert "pdf" in call_cmd
            assert str(sample_pptx_path) in call_cmd


def test_convert_one_output_missing_raises(tmp_path: Path, sample_pptx_path: Path) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    # Do not create the PDF so convert_one raises after run_soffice

    with patch("fast_pptx_pdf.converter.find_libreoffice", return_value="/usr/bin/soffice"):
        with patch("fast_pptx_pdf.converter.run_soffice"):
            with pytest.raises(RuntimeError, match="output not found"):
                convert_one(
                    sample_pptx_path,
                    output_dir=out_dir,
                    profile_url="file:///tmp/p",
                )

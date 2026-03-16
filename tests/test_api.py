"""Tests for api.convert_file and convert_folder."""

from pathlib import Path
from unittest.mock import patch

import pytest

from fast_pptx_pdf.api import convert_file, convert_folder


def test_convert_file_uses_temporary_profile(tmp_path: Path) -> None:
    pptx = tmp_path / "x.pptx"
    pptx.write_bytes(b"PK")
    (tmp_path / "x.pdf").touch()

    with patch("fast_pptx_pdf.api.convert_one") as convert_one_mock:
        convert_one_mock.return_value = tmp_path / "x.pdf"
        result = convert_file(pptx)
    assert result == tmp_path / "x.pdf"
    call_kw = convert_one_mock.call_args[1]
    assert "profile_url" in call_kw
    assert call_kw["profile_url"].startswith("file:///")


def test_convert_folder_not_dir_raises(tmp_path: Path) -> None:
    f = tmp_path / "f.pptx"
    f.touch()
    with pytest.raises(NotADirectoryError):
        convert_folder(f)


def test_convert_folder_empty_returns_empty_lists(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    successes, failures = convert_folder(tmp_path)
    assert successes == []
    assert failures == []


def test_convert_folder_default_workers(tmp_path: Path) -> None:
    (tmp_path / "a.pptx").touch()
    (tmp_path / "a.pdf").touch()

    with patch("fast_pptx_pdf.api.convert_folder_parallel") as parallel:
        parallel.return_value = ([tmp_path / "a.pdf"], [])
        convert_folder(tmp_path)
        # convert_folder_parallel(pptx_paths, workers, **kwargs) - workers is 2nd positional
        call_args = parallel.call_args[0]
        assert len(call_args) >= 2
        assert call_args[1] >= 1


def test_convert_folder_explicit_workers(tmp_path: Path) -> None:
    (tmp_path / "a.pptx").touch()
    (tmp_path / "a.pdf").touch()

    with patch("fast_pptx_pdf.api.convert_folder_parallel") as parallel:
        parallel.return_value = ([tmp_path / "a.pdf"], [])
        convert_folder(tmp_path, workers=4)
        assert parallel.call_args[0][1] == 4

"""Tests for pool.convert_folder_parallel."""

from concurrent.futures import Future
from pathlib import Path
from unittest.mock import patch

import pytest

from fast_pptx_pdf.pool import convert_folder_parallel, _convert_task


class _SyncExecutor:
    """Runs submitted tasks synchronously in the same process so mocks apply."""

    def __init__(self, max_workers: int = 1):
        self._max_workers = max_workers

    def submit(self, fn, *args, **kwargs):
        future: Future = Future()
        try:
            result = fn(*args, **kwargs)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        return future

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def test_convert_folder_parallel_empty() -> None:
    successes, failures = convert_folder_parallel([], workers=2)
    assert successes == []
    assert failures == []


def test_convert_task_returns_path_on_success(tmp_path: Path) -> None:
    pptx = tmp_path / "a.pptx"
    pptx.write_bytes(b"PK")
    pdf_path = tmp_path / "a.pdf"
    pdf_path.touch()

    with patch("fast_pptx_pdf.pool.convert_one", return_value=pdf_path):
        path_str, result = _convert_task(
            str(pptx), "file:///tmp/p", "/usr/bin/soffice", None, 60.0, 0
        )
    assert path_str == str(pptx)
    assert result == pdf_path


def test_convert_task_returns_exception_on_failure(tmp_path: Path) -> None:
    pptx = tmp_path / "a.pptx"
    pptx.touch()
    err = RuntimeError("conversion failed")

    with patch("fast_pptx_pdf.pool.convert_one", side_effect=err):
        path_str, result = _convert_task(
            str(pptx), "file:///tmp/p", "/usr/bin/soffice", None, 60.0, 0
        )
    assert path_str == str(pptx)
    assert result is err


def test_convert_folder_parallel_success(tmp_path: Path) -> None:
    (tmp_path / "a.pptx").touch()
    (tmp_path / "b.pptx").touch()
    (tmp_path / "a.pdf").touch()
    (tmp_path / "b.pdf").touch()
    paths = [tmp_path / "a.pptx", tmp_path / "b.pptx"]

    def fake_convert_one(*args, **kwargs):
        p = Path(args[0])
        return p.parent / (p.stem + ".pdf")

    with patch("fast_pptx_pdf.pool.find_libreoffice", return_value="/usr/bin/soffice"):
        with patch("fast_pptx_pdf.pool.convert_one", side_effect=fake_convert_one):
            with patch("fast_pptx_pdf.pool.ProcessPoolExecutor", _SyncExecutor):
                successes, failures = convert_folder_parallel(paths, workers=2, continue_on_error=True)
    assert len(successes) == 2
    assert len(failures) == 0


def test_convert_folder_parallel_continue_on_error(tmp_path: Path) -> None:
    (tmp_path / "a.pptx").touch()
    (tmp_path / "b.pptx").touch()
    paths = [tmp_path / "a.pptx", tmp_path / "b.pptx"]
    err = RuntimeError("fail")

    def fake_convert_one(path, **kwargs):
        if "a.pptx" in str(path):
            raise err
        return Path(path).parent / (Path(path).stem + ".pdf")

    with patch("fast_pptx_pdf.pool.find_libreoffice", return_value="/usr/bin/soffice"):
        with patch("fast_pptx_pdf.pool.convert_one", side_effect=fake_convert_one):
            with patch("fast_pptx_pdf.pool.ProcessPoolExecutor", _SyncExecutor):
                successes, failures = convert_folder_parallel(
                    paths, workers=2, continue_on_error=True
                )
    assert len(successes) == 1
    assert len(failures) == 1
    assert failures[0][1] is err


def test_convert_folder_parallel_raise_on_error(tmp_path: Path) -> None:
    (tmp_path / "a.pptx").touch()
    paths = [tmp_path / "a.pptx"]

    with patch("fast_pptx_pdf.pool.find_libreoffice", return_value="/usr/bin/soffice"):
        with patch("fast_pptx_pdf.pool.convert_one", side_effect=RuntimeError("fail")):
            with patch("fast_pptx_pdf.pool.ProcessPoolExecutor", _SyncExecutor):
                with pytest.raises(RuntimeError, match="fail"):
                    convert_folder_parallel(paths, workers=1, continue_on_error=False)

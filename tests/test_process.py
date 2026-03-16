"""Tests for process.run_soffice."""

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from fast_pptx_pdf.process import run_soffice
from fast_pptx_pdf.exceptions import ConversionError, ConversionTimeoutError


def test_run_soffice_success() -> None:
    with patch("subprocess.run") as m:
        m.return_value = MagicMock(returncode=0, stderr="", stdout="")
        run_soffice(["soffice", "--headless"], timeout=10, retries=0)
        m.assert_called_once()
        assert m.call_args[1]["timeout"] == 10


def test_run_soffice_nonzero_exit_raises() -> None:
    with patch("subprocess.run") as m:
        m.return_value = MagicMock(returncode=1, stderr="error", stdout="")
        with pytest.raises(ConversionError) as exc_info:
            run_soffice(["soffice", "--headless"], timeout=10, retries=0)
        assert exc_info.value.exit_code == 1
        assert "error" in (exc_info.value.stderr or "")


def test_run_soffice_timeout_raises() -> None:
    with patch("subprocess.run") as m:
        m.side_effect = subprocess.TimeoutExpired("soffice", 10)
        with pytest.raises(ConversionTimeoutError) as exc_info:
            run_soffice(["soffice"], timeout=10, retries=0)
        assert exc_info.value.timeout_seconds == 10


def test_run_soffice_retry_then_success() -> None:
    with patch("subprocess.run") as m:
        m.side_effect = [
            MagicMock(returncode=1, stderr="err", stdout=""),
            MagicMock(returncode=0, stderr="", stdout=""),
        ]
        run_soffice(["soffice"], timeout=10, retries=1)
        assert m.call_count == 2


def test_run_soffice_retry_still_fails() -> None:
    with patch("subprocess.run") as m:
        m.return_value = MagicMock(returncode=1, stderr="err", stdout="")
        with pytest.raises(ConversionError):
            run_soffice(["soffice"], timeout=10, retries=2)
        assert m.call_count == 3

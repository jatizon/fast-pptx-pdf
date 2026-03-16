"""Run soffice with timeout and optional retries."""

import subprocess
from typing import List, Optional

from fast_pptx_pdf.exceptions import ConversionError, ConversionTimeoutError


def run_soffice(
    cmd: List[str],
    *,
    timeout: float = 120.0,
    retries: int = 0,
) -> None:
    """
    Run a soffice command with timeout and optional retries.

    Args:
        cmd: Command and arguments as a list (e.g. ["soffice", "--headless", ...]).
        timeout: Maximum seconds to wait. Default 120.
        retries: Number of retries on timeout or non-zero exit. Default 0.

    Raises:
        ConversionTimeoutError: If the process does not complete within timeout.
        ConversionError: If the process exits with a non-zero code.
    """
    last_timeout: Optional[float] = None
    last_stderr: Optional[str] = None
    last_exit_code: Optional[int] = None

    for attempt in range(retries + 1):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as e:
            last_timeout = timeout
            if attempt == retries:
                raise ConversionTimeoutError(
                    f"Conversion timed out after {timeout} seconds",
                    timeout_seconds=timeout,
                ) from e
            continue

        if result.returncode != 0:
            last_stderr = result.stderr or result.stdout or ""
            last_exit_code = result.returncode
            if attempt == retries:
                msg = f"LibreOffice exited with code {result.returncode}"
                if last_stderr.strip():
                    msg += f". stderr: {last_stderr.strip()[:500]}"
                raise ConversionError(msg, stderr=last_stderr, exit_code=result.returncode)
            continue

        return

    # Should not reach here; for type checker
    raise ConversionError(
        "Conversion failed",
        stderr=last_stderr,
        exit_code=last_exit_code,
    )

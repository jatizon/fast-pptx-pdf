"""Custom exceptions for clear error handling."""

from typing import Optional


class FastPptxPdfError(Exception):
    """Base exception for fast_pptx_pdf."""


class LibreOfficeNotFoundError(FastPptxPdfError):
    """LibreOffice could not be found on the system."""


class ConversionTimeoutError(FastPptxPdfError):
    """Conversion did not complete within the timeout."""

    def __init__(self, message: str, timeout_seconds: Optional[float] = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class ConversionError(FastPptxPdfError):
    """Conversion failed (non-zero exit from LibreOffice)."""

    def __init__(self, message: str, stderr: Optional[str] = None, exit_code: Optional[int] = None):
        super().__init__(message)
        self.stderr = stderr
        self.exit_code = exit_code

"""fast_pptx_pdf: Convert PPTX to PDF using LibreOffice headless with parallel conversion."""

from fast_pptx_pdf.api import convert_file, convert_folder


def __get_version() -> str:
    try:
        from importlib.metadata import version
        return version("fast-pptx-pdf")
    except Exception:
        # Fallback when package is not installed (e.g. running from source)
        import re
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    m = re.match(r'^\s*version\s*=\s*["\']([^"\']+)["\']', line)
                    if m:
                        return m.group(1)
        except Exception:
            pass
        return "0.0.0+dev"


__version__ = __get_version()

__all__ = ["convert_file", "convert_folder", "__version__"]

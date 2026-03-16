"""Find LibreOffice executable (PATH, common install locations, env override)."""

import os
import glob
import shutil
from pathlib import Path

from fast_pptx_pdf.exceptions import LibreOfficeNotFoundError


def find_libreoffice(path_override: str | None = None) -> str:
    """
    Locate the LibreOffice soffice executable.

    Search order:
    1. User override (path_override or env FAST_PPTX_PDF_LIBREOFFICE).
    2. PATH (soffice or libreoffice).
    3. Common Windows install locations.
    4. Common Linux paths.

    Returns:
        Absolute path to the soffice executable.

    Raises:
        LibreOfficeNotFoundError: If LibreOffice could not be found.
    """
    env_path = os.environ.get("FAST_PPTX_PDF_LIBREOFFICE")
    explicit = path_override or env_path
    if explicit:
        p = Path(explicit).resolve()
        if p.is_file():
            return str(p)
        # Allow directory (e.g. LibreOffice/program); look for soffice inside
        if p.is_dir():
            for name in ("soffice", "soffice.exe"):
                candidate = p / name
                if candidate.is_file():
                    return str(candidate)
        raise LibreOfficeNotFoundError(
            f"LibreOffice path override is not a valid executable: {explicit}"
        )

    # Search PATH
    for name in ("soffice", "soffice.exe", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found

    # Windows: Program Files
    if os.name == "nt":
        for base in (
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        ):
            pattern = os.path.join(base, "LibreOffice*", "program", "soffice.exe")
            matches = glob.glob(pattern)
            if matches:
                return matches[0]

    # Linux / typical Unix
    for path in ("/usr/bin/soffice", "/usr/bin/libreoffice"):
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    raise LibreOfficeNotFoundError(
        "LibreOffice could not be found. Install LibreOffice or set "
        "FAST_PPTX_PDF_LIBREOFFICE to the path to soffice (or its program directory)."
    )

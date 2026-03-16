"""Single-file PPTX to PDF conversion via LibreOffice headless."""

from pathlib import Path
from typing import Optional, Union

from fast_pptx_pdf.libreoffice import find_libreoffice
from fast_pptx_pdf.process import run_soffice


def convert_one(
    pptx_path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
    libreoffice_path: Optional[str] = None,
    profile_url: Optional[str] = None,
    timeout: float = 120.0,
    retries: int = 0,
) -> Path:
    """
    Convert a single PPTX file to PDF in the same directory (or output_dir).

    Args:
        pptx_path: Path to the .pptx file.
        output_dir: Directory for the output PDF. Default: same as input file.
        libreoffice_path: Path to soffice. Default: auto-detect.
        profile_url: UserInstallation URL for soffice. Default: none (use default profile).
        timeout: Max seconds per conversion.
        retries: Number of retries on failure.

    Returns:
        Path to the created PDF file.

    Raises:
        LibreOfficeNotFoundError: If LibreOffice could not be found.
        ConversionTimeoutError: If conversion times out.
        ConversionError: If conversion fails.
    """
    path = Path(pptx_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Not a file: {path}")
    if path.suffix.lower() != ".pptx":
        raise ValueError(f"Expected .pptx file, got: {path.suffix}")

    out_dir = Path(output_dir).resolve() if output_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    soffice = find_libreoffice(libreoffice_path)

    cmd = [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir)]
    if profile_url:
        cmd.extend(["-env:UserInstallation=" + profile_url])
    cmd.append(str(path))

    run_soffice(cmd, timeout=timeout, retries=retries)

    pdf_path = out_dir / (path.stem + ".pdf")
    if not pdf_path.is_file():
        raise RuntimeError(f"Conversion completed but output not found: {pdf_path}")
    return pdf_path

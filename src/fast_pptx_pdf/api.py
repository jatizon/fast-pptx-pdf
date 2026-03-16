"""Public API: convert_file and convert_folder."""

import os
from pathlib import Path
from typing import Callable, List, Optional, Set, Tuple, Union

from fast_pptx_pdf.converter import convert_one
from fast_pptx_pdf.profiles import temporary_profile
from fast_pptx_pdf.pool import convert_folder_parallel


def convert_file(
    path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
    libreoffice_path: Optional[str] = None,
    timeout: float = 120.0,
    retries: int = 0,
) -> Path:
    """
    Convert a single PPTX file to PDF.

    Args:
        path: Path to the .pptx file.
        output_dir: Directory for the output PDF. Default: same as input file.
        libreoffice_path: Path to LibreOffice soffice. Default: auto-detect.
        timeout: Max seconds per conversion.
        retries: Number of retries on failure.

    Returns:
        Path to the created PDF file.
    """
    with temporary_profile() as profile_dir:
        profile_url = Path(profile_dir).resolve().as_uri()
        return convert_one(
            path,
            output_dir=output_dir,
            libreoffice_path=libreoffice_path,
            profile_url=profile_url,
            timeout=timeout,
            retries=retries,
        )


def convert_folder(
    path: Union[str, Path],
    *,
    output_dir: Optional[Union[str, Path]] = None,
    workers: Optional[int] = None,
    libreoffice_path: Optional[str] = None,
    timeout: float = 120.0,
    retries: int = 0,
    continue_on_error: bool = False,
    show_progress: bool = False,
    progress_callback: Optional[Callable[[Path], None]] = None,
) -> Tuple[List[Path], List[Tuple[Path, Exception]]]:
    """
    Convert all PPTX files in a folder to PDF in parallel.

    Args:
        path: Path to a directory containing .pptx files.
        output_dir: Directory for output PDFs. Default: same as input folder.
        workers: Number of worker processes. Default: min(cpu_count, number of files).
        libreoffice_path: Path to LibreOffice soffice. Default: auto-detect.
        timeout: Max seconds per conversion.
        retries: Retries per conversion.
        continue_on_error: If False, raise on first failure. If True, return successes and failures.
        show_progress: If True, show a progress bar using tqdm (if installed).
        progress_callback: Optional callback called with each PPTX Path after it finishes
            (success or failure).

    Returns:
        (success_list, failure_list). success_list is list of output PDF paths;
        failure_list is list of (pptx_path, exception).
        If continue_on_error is False and any conversion fails, raises the first exception.
    """
    folder = Path(path).resolve()
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")

    all_pptx = sorted(folder.glob("*.pptx")) + sorted(folder.glob("*.PPTX"))
    seen: Set[Path] = set()
    pptx_paths = []
    for p in all_pptx:
        r = p.resolve()
        if r not in seen:
            seen.add(r)
            pptx_paths.append(p)
    if not pptx_paths:
        return ([], [])

    cpu_count = os.cpu_count() or 4
    if workers is None:
        workers = min(cpu_count, len(pptx_paths))
    workers = max(1, workers)

    return convert_folder_parallel(
        pptx_paths,
        workers,
        output_dir=output_dir,
        libreoffice_path=libreoffice_path,
        timeout=timeout,
        retries=retries,
        continue_on_error=continue_on_error,
        show_progress=show_progress,
        progress_callback=progress_callback,
    )
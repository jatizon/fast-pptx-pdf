"""Worker pool for parallel PPTX to PDF conversion with per-worker profiles."""

import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, List, Optional, Tuple, Union

from fast_pptx_pdf.converter import convert_one
from fast_pptx_pdf.libreoffice import find_libreoffice
from fast_pptx_pdf.profiles import ProfileManager


def _convert_task(
    pptx_path: str,
    profile_url: str,
    libreoffice_path: Optional[str],
    output_dir: Optional[str],
    timeout: float,
    retries: int,
) -> Tuple[str, Union[Path, Exception]]:
    """
    Run in a worker process: convert one file with the given profile.
    Returns (pptx_path, output_path or exception).
    """
    try:
        out = convert_one(
            pptx_path,
            profile_url=profile_url,
            libreoffice_path=libreoffice_path,
            output_dir=output_dir,
            timeout=timeout,
            retries=retries,
        )
        return (pptx_path, out)
    except Exception as e:
        return (pptx_path, e)


def convert_folder_parallel(
    pptx_paths: List[Path],
    workers: int,
    *,
    output_dir: Optional[Union[str, Path]] = None,
    libreoffice_path: Optional[str] = None,
    timeout: float = 120.0,
    retries: int = 0,
    continue_on_error: bool = False,
    show_progress: bool = False,
    progress_callback: Optional[Callable[[Path], None]] = None,
) -> Tuple[List[Path], List[Tuple[Path, Exception]]]:
    """
    Convert multiple PPTX files in parallel, each worker using its own profile.

    Args:
        pptx_paths: List of paths to .pptx files.
        workers: Number of worker processes.
        output_dir: Directory for output PDFs. Default: same directory as each input file.
        libreoffice_path: Optional path to soffice (found once in main process).
        timeout: Timeout per conversion in seconds.
        retries: Retries per conversion.
        continue_on_error: If False, raise on first failure. If True, return successes and failures.

    Returns:
        (success_list, failure_list). success_list is list of output PDF paths;
        failure_list is list of (pptx_path, exception).
        If continue_on_error is False and any conversion fails, raises the first exception instead.
    """
    if not pptx_paths:
        return ([], [])

    lo_path = libreoffice_path if libreoffice_path is not None else find_libreoffice(None)
    n = min(workers, len(pptx_paths))
    str_paths = [str(p) for p in pptx_paths]

    out_dir_str: Optional[str] = str(output_dir) if output_dir is not None else None

    with ProfileManager(n) as profiles:
        profile_urls = [profiles.get_profile_url(i) for i in range(n)]
        tasks = [
            (path, profile_urls[i % n])
            for i, path in enumerate(str_paths)
        ]

        successes: List[Path] = []
        failures: List[Tuple[Path, Exception]] = []
        first_error: Optional[Exception] = None

        with ProcessPoolExecutor(max_workers=n) as executor:
            future_to_path = {
                executor.submit(
                    _convert_task,
                    path,
                    url,
                    lo_path,
                    out_dir_str,
                    timeout,
                    retries,
                ): path
                for path, url in tasks
            }

            for future in as_completed(future_to_path):
                path_str = future_to_path[future]
                path = Path(path_str)
                try:
                    _, result = future.result()
                    if isinstance(result, Exception):
                        if not continue_on_error and first_error is None:
                            first_error = result
                        failures.append((path, result))
                    else:
                        successes.append(result)
                except Exception as e:
                    if not continue_on_error and first_error is None:
                        first_error = e
                    failures.append((path, e))

                if progress_callback is not None:
                    progress_callback(path)

        if first_error is not None and not continue_on_error:
            raise first_error

    return (successes, failures)

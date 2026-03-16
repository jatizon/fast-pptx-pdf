# fast-pptx-pdf

[![PyPI version](https://img.shields.io/pypi/v/fast-pptx-pdf.svg)](https://pypi.org/project/fast-pptx-pdf/)
[![Python versions](https://img.shields.io/pypi/pyversions/fast-pptx-pdf.svg)](https://pypi.org/project/fast-pptx-pdf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/your-org/fast-pptx-pdf/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/fast-pptx-pdf/actions)

Convert PPTX files to PDF using LibreOffice in headless mode, with **safe parallel conversion** via per-worker profiles.

- **Simple API**: `convert_file(path)` and `convert_folder(path, workers=8)`.
- **CLI**: `fast-pptx-pdf file.pptx` or `fast-pptx-pdf folder/ --workers 8`.
- **No profile locking**: Each worker uses its own LibreOffice profile in a temp directory.
- **Robust**: Timeouts, optional retries, and clear errors.

Python cannot natively render PowerPoint files; this library uses the LibreOffice command-line interface. COM automation (Windows) is not thread-safe; LibreOffice headless runs one process per conversion and is suitable for parallelism when each process has a separate profile.

## Requirements

- **Python** 3.8+
- **LibreOffice** installed and on `PATH`, or set `FAST_PPTX_PDF_LIBREOFFICE` to the path to `soffice` (or its `program` directory).

### Installing LibreOffice

- **Windows**: [Download](https://www.libreoffice.org/download/download/) the installer, or use `winget install TheDocumentFoundation.LibreOffice`.
- **Linux**: e.g. `sudo apt install libreoffice` (Debian/Ubuntu) or your distribution’s package.

## Install

```bash
pip install fast-pptx-pdf
```

## Usage

### Python API

```python
from fast_pptx_pdf import convert_file, convert_folder

# Single file (output PDF next to the PPTX by default)
pdf_path = convert_file("slides/presentation.pptx")
# Optional: output directory, timeout, retries
pdf_path = convert_file("deck.pptx", output_dir="pdfs/", timeout=60, retries=1)

# Folder: convert all .pptx in parallel (workers default: min(cpu_count, number of files))
successes, failures = convert_folder("slides/")
successes, failures = convert_folder("slides/", workers=8, continue_on_error=True)
```

### CLI

```bash
# Single file
fast-pptx-pdf presentation.pptx

# Folder (default workers)
fast-pptx-pdf slides/

# Folder with 8 workers
fast-pptx-pdf slides/ --workers 8

# Optional: timeout, retries, LibreOffice path, continue on error
fast-pptx-pdf slides/ --workers 4 --timeout 60 --retries 1 --continue-on-error
fast-pptx-pdf file.pptx --libreoffice "C:\Program Files\LibreOffice\program\soffice.exe"
```

## Configuration

- **LibreOffice path**: Set the environment variable `FAST_PPTX_PDF_LIBREOFFICE` to the full path to `soffice` or to the LibreOffice `program` directory. The library also searches `PATH` and common install locations (e.g. Windows `Program Files`, Linux `/usr/bin/soffice`).
- **Workers**: For `convert_folder`, if `workers` is not set, it uses `min(cpu_count, number_of_pptx_files)`.

## License

MIT. See [LICENSE](LICENSE).

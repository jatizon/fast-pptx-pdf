"""CLI for fast-pptx-pdf."""

import argparse
import sys
from pathlib import Path

from fast_pptx_pdf.api import convert_file, convert_folder
from fast_pptx_pdf.exceptions import FastPptxPdfError, LibreOfficeNotFoundError


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert PPTX files to PDF using LibreOffice headless (supports parallel conversion).",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to a .pptx file or a directory containing .pptx files",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        metavar="DIR",
        dest="output_dir",
        help="Output directory for PDFs (folder mode). Default: same as input folder",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        metavar="N",
        help="Number of parallel workers (folder only). Default: min(cpu_count, number of files)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        metavar="SECS",
        help="Timeout per conversion in seconds (default: 120)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=0,
        metavar="N",
        help="Retries per conversion (default: 0)",
    )
    parser.add_argument(
        "--libreoffice",
        type=Path,
        default=None,
        metavar="PATH",
        help="Path to LibreOffice soffice executable (default: auto-detect)",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="On folder conversion, continue on errors and report at the end",
    )
    args = parser.parse_args()

    path = args.path.resolve()
    lo_path = str(args.libreoffice) if args.libreoffice else None

    try:
        if path.is_file():
            if path.suffix.lower() != ".pptx":
                print(f"Error: expected .pptx file, got {path.suffix}", file=sys.stderr)
                sys.exit(1)
            out = convert_file(
                path,
                output_dir=args.output_dir,
                libreoffice_path=lo_path,
                timeout=args.timeout,
                retries=args.retries,
            )
            print(out)
        elif path.is_dir():
            successes, failures = convert_folder(
                path,
                output_dir=args.output_dir,
                workers=args.workers,
                libreoffice_path=lo_path,
                timeout=args.timeout,
                retries=args.retries,
                continue_on_error=args.continue_on_error,
            )
            for p in successes:
                print(p)
            if failures:
                for pptx_path, err in failures:
                    print(f"Failed: {pptx_path} - {err}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Error: path does not exist: {path}", file=sys.stderr)
            sys.exit(1)
    except LibreOfficeNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FastPptxPdfError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

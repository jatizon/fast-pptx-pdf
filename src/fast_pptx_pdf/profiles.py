"""Manage per-worker LibreOffice profile directories to avoid profile locking."""

import atexit
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class ProfileManager:
    """
    Create and manage N LibreOffice profile directories under a single temp parent.

    Each worker uses one profile dir (profile_0, profile_1, ...). Cleanup removes
    the entire parent directory.
    """

    def __init__(self, num_profiles: int) -> None:
        if num_profiles < 1:
            raise ValueError("num_profiles must be at least 1")
        self._num_profiles = num_profiles
        self._root: Path | None = None
        self._created = False

    def create(self) -> None:
        """Create the parent temp dir and profile_0 .. profile_{N-1} subdirs."""
        if self._created:
            return
        self._root = Path(tempfile.mkdtemp(prefix="fast_pptx_pdf_profiles_"))
        for i in range(self._num_profiles):
            (self._root / f"profile_{i}").mkdir(parents=True, exist_ok=True)
        self._created = True
        atexit.register(self.cleanup)

    def get_profile_dir(self, index: int) -> Path:
        """Return the path for profile index (0..num_profiles-1)."""
        if not self._created or self._root is None:
            raise RuntimeError("ProfileManager.create() must be called first")
        if index < 0 or index >= self._num_profiles:
            raise ValueError(f"Profile index must be 0..{self._num_profiles - 1}, got {index}")
        return self._root / f"profile_{index}"

    def get_profile_url(self, index: int) -> str:
        """
        Return the UserInstallation URL for soffice -env:UserInstallation=...
        Uses file:/// with normalized path (Windows: drive letter as /C/...).
        """
        path = self.get_profile_dir(index).resolve()
        # path.as_uri() gives file:///C:/path on Windows, file:///path on Unix
        return path.as_uri()

    def cleanup(self) -> None:
        """Remove the parent temp directory and all profile subdirs."""
        if self._root is not None and self._root.exists():
            try:
                shutil.rmtree(self._root, ignore_errors=True)
            except OSError:
                pass
            self._root = None
        self._created = False
        try:
            atexit.unregister(self.cleanup)
        except Exception:
            pass

    def __enter__(self) -> "ProfileManager":
        self.create()
        return self

    def __exit__(self, *args: object) -> None:
        self.cleanup()


@contextmanager
def temporary_profile() -> Iterator[Path]:
    """
    Context manager that creates a single temporary profile dir for one-off conversion.
    Yields the profile path; cleans up on exit.
    """
    root = Path(tempfile.mkdtemp(prefix="fast_pptx_pdf_profile_"))
    try:
        yield root
    finally:
        try:
            shutil.rmtree(root, ignore_errors=True)
        except OSError:
            pass

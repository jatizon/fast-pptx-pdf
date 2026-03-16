"""Tests for profiles.ProfileManager and temporary_profile."""

from pathlib import Path

import pytest

from fast_pptx_pdf.profiles import ProfileManager, temporary_profile


def test_profile_manager_num_profiles_must_be_positive() -> None:
    with pytest.raises(ValueError):
        ProfileManager(0)
    with pytest.raises(ValueError):
        ProfileManager(-1)


def test_profile_manager_create_and_get_dir() -> None:
    mgr = ProfileManager(3)
    mgr.create()
    try:
        for i in range(3):
            d = mgr.get_profile_dir(i)
            assert d.name == f"profile_{i}"
            assert d.parent == mgr.get_profile_dir(0).parent
            assert d.exists()
        with pytest.raises(ValueError):
            mgr.get_profile_dir(3)
        with pytest.raises(ValueError):
            mgr.get_profile_dir(-1)
    finally:
        mgr.cleanup()


def test_profile_manager_get_dir_without_create_raises() -> None:
    mgr = ProfileManager(2)
    with pytest.raises(RuntimeError):
        mgr.get_profile_dir(0)
    mgr.create()
    mgr.get_profile_dir(0)
    mgr.cleanup()
    with pytest.raises(RuntimeError):
        mgr.get_profile_dir(0)


def test_profile_manager_get_profile_url() -> None:
    mgr = ProfileManager(1)
    mgr.create()
    try:
        url = mgr.get_profile_url(0)
        assert url.startswith("file:///")
        assert "profile_0" in url
    finally:
        mgr.cleanup()


def test_profile_manager_context_manager() -> None:
    with ProfileManager(2) as mgr:
        root = mgr.get_profile_dir(0).parent
        assert root.exists()
        assert (root / "profile_0").exists()
        assert (root / "profile_1").exists()
    assert not root.exists()


def test_temporary_profile_context_manager() -> None:
    with temporary_profile() as d:
        assert d.exists()
        assert d.is_dir()
        path = d
    assert not path.exists()

"""Tests for profile import/export functionality."""
import os
import pytest
from click.testing import CliRunner
from envoy.profiles import get_profiles_dir, save_profile, list_profiles
from envoy.import_export_profile import (
    export_profile, import_profile, export_all_profiles, import_all_profiles
)


@pytest.fixture(autouse=True)
def set_profiles_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.profiles.PROFILES_DIR", str(tmp_path / "profiles"))
    monkeypatch.setattr("envoy.import_export_profile.get_profiles_dir",
                        lambda: str(tmp_path / "profiles"))
    os.makedirs(str(tmp_path / "profiles"), exist_ok=True)
    return tmp_path


def test_export_and_import_roundtrip(tmp_path):
    save_profile("prod", {"ciphertext": "abc", "salt": "xyz"})
    archive = str(tmp_path / "prod.envoy")
    export_profile("prod", archive)
    assert os.path.exists(archive)
    # Remove and reimport
    from envoy.profiles import delete_profile
    delete_profile("prod")
    assert "prod" not in list_profiles()
    name = import_profile(archive)
    assert name == "prod"
    assert "prod" in list_profiles()


def test_export_missing_profile_raises(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        export_profile("nonexistent", str(tmp_path / "out.envoy"))


def test_import_overwrite_false_raises(tmp_path):
    save_profile("dev", {"ciphertext": "aaa", "salt": "bbb"})
    archive = str(tmp_path / "dev.envoy")
    export_profile("dev", archive)
    with pytest.raises(FileExistsError):
        import_profile(archive, overwrite=False)


def test_import_overwrite_true_replaces(tmp_path):
    save_profile("dev", {"ciphertext": "old", "salt": "s"})
    archive = str(tmp_path / "dev.envoy")
    export_profile("dev", archive)
    save_profile("dev", {"ciphertext": "new", "salt": "s"})
    import_profile(archive, overwrite=True)
    from envoy.profiles import load_profile
    data = load_profile("dev")
    assert data["ciphertext"] == "old"


def test_export_all_and_import_all(tmp_path):
    save_profile("a", {"ciphertext": "1", "salt": "s"})
    save_profile("b", {"ciphertext": "2", "salt": "s"})
    archive = str(tmp_path / "all.envoy")
    names = export_all_profiles(archive)
    assert set(names) == {"a", "b"}
    from envoy.profiles import delete_profile
    delete_profile("a")
    delete_profile("b")
    imported = import_all_profiles(archive)
    assert set(imported) == {"a", "b"}


def test_import_all_skips_existing(tmp_path):
    save_profile("x", {"ciphertext": "v", "salt": "s"})
    archive = str(tmp_path / "x.envoy")
    export_all_profiles(archive)
    imported = import_all_profiles(archive, overwrite=False)
    assert imported == []

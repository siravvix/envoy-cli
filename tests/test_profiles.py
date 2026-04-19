"""Tests for envoy profile management."""

import pytest
import os
from pathlib import Path
from envoy.profiles import (
    list_profiles,
    save_profile,
    load_profile,
    delete_profile,
)


@pytest.fixture(autouse=True)
def set_profiles_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_PROFILES_DIR", str(tmp_path / "profiles"))


@pytest.fixture
def saved_profile(tmp_path):
    """Create and save a basic profile, returning its name and env file path."""
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    save_profile("fixture_profile", str(env_file))
    return {"name": "fixture_profile", "env_path": env_file}


def test_list_profiles_empty():
    assert list_profiles() == []


def test_save_and_list_profiles(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    save_profile("dev", str(env_file))
    profiles = list_profiles()
    assert "dev" in profiles


def test_load_profile(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    save_profile("staging", str(env_file), encrypted=True)
    profile = load_profile("staging")
    assert profile["name"] == "staging"
    assert profile["encrypted"] is True
    assert profile["env_path"] == str(env_file.resolve())


def test_load_profile_not_found():
    with pytest.raises(FileNotFoundError, match="Profile 'ghost' not found."):
        load_profile("ghost")


def test_delete_profile(saved_profile):
    assert saved_profile["name"] in list_profiles()
    delete_profile(saved_profile["name"])
    assert saved_profile["name"] not in list_profiles()


def test_delete_profile_not_found():
    with pytest.raises(FileNotFoundError, match="Profile 'none' not found."):
        delete_profile("none")


def test_multiple_profiles(tmp_path):
    for name in ["dev", "staging", "prod"]:
        env_file = tmp_path / f".env.{name}"
        env_file.write_text(f"ENV={name}\n")
        save_profile(name, str(env_file))
    profiles = list_profiles()
    assert set(profiles) == {"dev", "staging", "prod"}


def test_load_profile_defaults_to_unencrypted(saved_profile):
    """Profiles saved without explicit encryption should default to unencrypted."""
    profile = load_profile(saved_profile["name"])
    assert profile["encrypted"] is False

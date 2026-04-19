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


def test_delete_profile(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    save_profile("prod", str(env_file))
    assert "prod" in list_profiles()
    delete_profile("prod")
    assert "prod" not in list_profiles()


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

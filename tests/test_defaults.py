"""Tests for envoy.defaults module."""

import pytest
from pathlib import Path
from unittest.mock import patch

from envoy.defaults import (
    load_defaults,
    save_defaults,
    set_default,
    remove_default,
    get_default,
    apply_defaults,
    get_defaults_path,
)


@pytest.fixture(autouse=True)
def set_profiles_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.profiles.PROFILES_DIR", tmp_path)
    monkeypatch.setattr("envoy.defaults.get_defaults_path",
                        lambda profile: tmp_path / profile / "defaults.json")


PROFILE = "staging"


def test_load_defaults_empty(tmp_path):
    result = load_defaults(PROFILE)
    assert result == {}


def test_set_and_load_default(tmp_path):
    set_default(PROFILE, "LOG_LEVEL", "info")
    defaults = load_defaults(PROFILE)
    assert defaults["LOG_LEVEL"] == "info"


def test_set_default_empty_key_raises():
    with pytest.raises(ValueError, match="Key must not be empty"):
        set_default(PROFILE, "", "value")


def test_set_default_overwrites_existing():
    set_default(PROFILE, "TIMEOUT", "30")
    set_default(PROFILE, "TIMEOUT", "60")
    assert get_default(PROFILE, "TIMEOUT") == "60"


def test_get_default_missing_key():
    result = get_default(PROFILE, "NONEXISTENT")
    assert result is None


def test_remove_default_existing():
    set_default(PROFILE, "DEBUG", "true")
    removed = remove_default(PROFILE, "DEBUG")
    assert removed is True
    assert get_default(PROFILE, "DEBUG") is None


def test_remove_default_nonexistent():
    removed = remove_default(PROFILE, "GHOST_KEY")
    assert removed is False


def test_apply_defaults_fills_missing_keys():
    set_default(PROFILE, "LOG_LEVEL", "warn")
    set_default(PROFILE, "TIMEOUT", "30")
    env = {"APP_NAME": "myapp", "TIMEOUT": "60"}
    result = apply_defaults(PROFILE, env)
    assert result["LOG_LEVEL"] == "warn"   # filled from defaults
    assert result["TIMEOUT"] == "60"       # existing value preserved
    assert result["APP_NAME"] == "myapp"   # unchanged


def test_apply_defaults_does_not_mutate_original():
    set_default(PROFILE, "INJECTED", "yes")
    env = {"KEY": "val"}
    result = apply_defaults(PROFILE, env)
    assert "INJECTED" not in env
    assert "INJECTED" in result


def test_save_and_load_multiple_defaults():
    data = {"A": "1", "B": "2", "C": "3"}
    save_defaults(PROFILE, data)
    loaded = load_defaults(PROFILE)
    assert loaded == data

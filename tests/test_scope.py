"""Tests for envoy/scope.py"""

import pytest
from pathlib import Path
import envoy.scope as scope_mod


@pytest.fixture(autouse=True)
def set_scopes_dir(tmp_path):
    original = scope_mod._scopes_dir
    scope_mod._scopes_dir = tmp_path
    yield
    scope_mod._scopes_dir = original


def test_load_scopes_empty():
    assert scope_mod.load_scopes() == {}


def test_add_key_to_scope_new():
    scope_mod.add_key_to_scope("dev", "DB_HOST")
    assert "DB_HOST" in scope_mod.get_scope_keys("dev")


def test_add_key_to_scope_idempotent():
    scope_mod.add_key_to_scope("dev", "DB_HOST")
    scope_mod.add_key_to_scope("dev", "DB_HOST")
    assert scope_mod.get_scope_keys("dev").count("DB_HOST") == 1


def test_add_key_empty_raises():
    with pytest.raises(ValueError):
        scope_mod.add_key_to_scope("", "DB_HOST")
    with pytest.raises(ValueError):
        scope_mod.add_key_to_scope("dev", "")


def test_remove_key_existing():
    scope_mod.add_key_to_scope("dev", "API_KEY")
    result = scope_mod.remove_key_from_scope("dev", "API_KEY")
    assert result is True
    assert "API_KEY" not in scope_mod.get_scope_keys("dev")


def test_remove_key_missing_returns_false():
    result = scope_mod.remove_key_from_scope("dev", "NONEXISTENT")
    assert result is False


def test_remove_last_key_deletes_scope():
    scope_mod.add_key_to_scope("staging", "ONLY_KEY")
    scope_mod.remove_key_from_scope("staging", "ONLY_KEY")
    assert "staging" not in scope_mod.list_scopes()


def test_list_scopes():
    scope_mod.add_key_to_scope("dev", "A")
    scope_mod.add_key_to_scope("prod", "B")
    scopes = scope_mod.list_scopes()
    assert "dev" in scopes
    assert "prod" in scopes


def test_filter_env_by_scope():
    env = {"DB_HOST": "localhost", "API_KEY": "secret", "PORT": "8080"}
    scope_mod.add_key_to_scope("backend", "DB_HOST")
    scope_mod.add_key_to_scope("backend", "PORT")
    result = scope_mod.filter_env_by_scope(env, "backend")
    assert result == {"DB_HOST": "localhost", "PORT": "8080"}
    assert "API_KEY" not in result


def test_filter_env_by_scope_no_match():
    env = {"X": "1"}
    result = scope_mod.filter_env_by_scope(env, "empty_scope")
    assert result == {}


def test_delete_scope():
    scope_mod.add_key_to_scope("tmp", "KEY")
    assert scope_mod.delete_scope("tmp") is True
    assert "tmp" not in scope_mod.list_scopes()


def test_delete_scope_missing():
    assert scope_mod.delete_scope("ghost") is False

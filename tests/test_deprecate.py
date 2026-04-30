"""Tests for envoy.deprecate and envoy.cli_deprecate."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from pathlib import Path

from envoy.deprecate import (
    deprecate_key,
    undeprecate_key,
    is_deprecated,
    check_env_for_deprecated,
    format_deprecation_results,
    load_deprecations,
)
from envoy.cli_deprecate import deprecate_cli


@pytest.fixture(autouse=True)
def set_profiles_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.deprecate.get_profiles_dir", lambda: tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_deprecate_key_and_is_deprecated():
    deprecate_key("OLD_KEY", reason="No longer used")
    assert is_deprecated("OLD_KEY") is True


def test_deprecate_key_with_replacement():
    deprecate_key("LEGACY_TOKEN", reason="Replaced", replacement="NEW_TOKEN")
    data = load_deprecations()
    assert data["LEGACY_TOKEN"]["replacement"] == "NEW_TOKEN"


def test_undeprecate_existing():
    deprecate_key("TEMP_KEY")
    result = undeprecate_key("TEMP_KEY")
    assert result is True
    assert is_deprecated("TEMP_KEY") is False


def test_undeprecate_missing_returns_false():
    result = undeprecate_key("NONEXISTENT")
    assert result is False


def test_deprecate_empty_key_raises():
    with pytest.raises(ValueError):
        deprecate_key("")


def test_check_env_finds_deprecated_keys():
    deprecate_key("OLD_DB_URL", reason="Use DATABASE_URL")
    env = {"OLD_DB_URL": "postgres://...", "NEW_KEY": "value"}
    results = check_env_for_deprecated(env)
    assert len(results) == 1
    assert results[0]["key"] == "OLD_DB_URL"


def test_check_env_no_deprecated():
    env = {"CLEAN_KEY": "value"}
    results = check_env_for_deprecated(env)
    assert results == []


def test_format_deprecation_results_empty():
    output = format_deprecation_results([])
    assert "No deprecated" in output


def test_format_deprecation_results_with_entries():
    results = [
        {"key": "OLD_KEY", "reason": "Obsolete", "replacement": "NEW_KEY"}
    ]
    output = format_deprecation_results(results)
    assert "OLD_KEY" in output
    assert "Obsolete" in output
    assert "NEW_KEY" in output


def test_cli_add_command(runner, tmp_path):
    with runner.isolated_filesystem():
        result = runner.invoke(deprecate_cli, ["add", "MY_KEY", "--reason", "old"])
        assert result.exit_code == 0
        assert "MY_KEY" in result.output


def test_cli_list_command(runner):
    deprecate_key("LIST_KEY", reason="test reason")
    result = runner.invoke(deprecate_cli, ["list"])
    assert result.exit_code == 0
    assert "LIST_KEY" in result.output


def test_cli_check_command_clean(runner, tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("CLEAN=value\n")
    result = runner.invoke(deprecate_cli, ["check", str(env_path)])
    assert result.exit_code == 0
    assert "No deprecated" in result.output

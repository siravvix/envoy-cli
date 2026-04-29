"""Tests for envoy.cli_resolve CLI commands."""

import pytest
from click.testing import CliRunner
from envoy.cli_resolve import resolve_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    base.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=development\n")
    prod = tmp_path / "prod.env"
    prod.write_text("DB_HOST=prod.db\nAPI_KEY=secret\n")
    return str(base), str(prod)


def test_get_command_last_file_wins(runner, env_files):
    base, prod = env_files
    result = runner.invoke(resolve_cli, ["get", "DB_HOST", base, prod])
    assert result.exit_code == 0
    assert "prod.db" in result.output


def test_get_command_key_only_in_first(runner, env_files):
    base, prod = env_files
    result = runner.invoke(resolve_cli, ["get", "DB_PORT", base, prod])
    assert result.exit_code == 0
    assert "5432" in result.output


def test_get_command_key_not_found(runner, env_files):
    base, prod = env_files
    result = runner.invoke(resolve_cli, ["get", "NONEXISTENT", base, prod])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_get_command_missing_file(runner, tmp_path):
    result = runner.invoke(resolve_cli, ["get", "KEY", str(tmp_path / "ghost.env")])
    assert result.exit_code != 0
    assert "File not found" in result.output


def test_trace_command_shows_sources(runner, env_files):
    base, prod = env_files
    result = runner.invoke(resolve_cli, ["trace", "DB_HOST", base, prod])
    assert result.exit_code == 0
    assert "localhost" in result.output
    assert "prod.db" in result.output
    assert "active" in result.output


def test_trace_command_key_not_in_any(runner, env_files):
    base, prod = env_files
    result = runner.invoke(resolve_cli, ["trace", "GHOST", base, prod])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_missing_command_reports_absent_keys(runner, env_files):
    base, prod = env_files
    result = runner.invoke(resolve_cli, ["missing", "DB_HOST", "UNDEFINED_KEY", "-f", base, "-f", prod])
    assert result.exit_code == 0
    assert "MISSING: UNDEFINED_KEY" in result.output
    assert "DB_HOST" not in result.output


def test_missing_command_all_present(runner, env_files):
    base, _ = env_files
    result = runner.invoke(resolve_cli, ["missing", "DB_HOST", "-f", base])
    assert result.exit_code == 0
    assert "All keys are defined" in result.output

"""Tests for envoy.cli_rename CLI commands."""

import pytest
from click.testing import CliRunner
from envoy.cli_rename import rename_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("APP_HOST=localhost\nAPP_PORT=8080\nDEBUG=true\n")
    return str(f)


def test_rename_key_command(runner, env_file):
    result = runner.invoke(rename_cli, ["key", env_file, "APP_HOST", "HOST"])
    assert result.exit_code == 0
    assert "Renamed 'APP_HOST' -> 'HOST'" in result.output
    with open(env_file) as f:
        content = f.read()
    assert "HOST=localhost" in content
    assert "APP_HOST" not in content


def test_rename_key_missing(runner, env_file):
    result = runner.invoke(rename_cli, ["key", env_file, "MISSING", "NEW"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_rename_key_conflict_no_overwrite(runner, env_file):
    result = runner.invoke(rename_cli, ["key", env_file, "APP_HOST", "APP_PORT"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_rename_key_conflict_with_overwrite(runner, env_file):
    result = runner.invoke(
        rename_cli, ["key", env_file, "APP_HOST", "APP_PORT", "--overwrite"]
    )
    assert result.exit_code == 0
    with open(env_file) as f:
        content = f.read()
    assert "APP_PORT=localhost" in content


def test_copy_key_command(runner, env_file):
    result = runner.invoke(rename_cli, ["copy", env_file, "APP_HOST", "HOST_COPY"])
    assert result.exit_code == 0
    assert "Copied 'APP_HOST' -> 'HOST_COPY'" in result.output
    with open(env_file) as f:
        content = f.read()
    assert "HOST_COPY=localhost" in content
    assert "APP_HOST=localhost" in content


def test_copy_key_missing(runner, env_file):
    result = runner.invoke(rename_cli, ["copy", env_file, "NOPE", "DEST"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_copy_key_conflict_with_overwrite(runner, env_file):
    result = runner.invoke(
        rename_cli, ["copy", env_file, "APP_HOST", "DEBUG", "--overwrite"]
    )
    assert result.exit_code == 0
    with open(env_file) as f:
        content = f.read()
    assert "DEBUG=localhost" in content

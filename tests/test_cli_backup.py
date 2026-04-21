"""Tests for envoy.cli_backup CLI commands."""

import os
import pytest
from click.testing import CliRunner
from envoy.cli_backup import backup_cli
import envoy.backup as backup_mod


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def set_backup_dir(tmp_path):
    backup_mod._backup_dir_override = str(tmp_path / "backups")
    yield
    backup_mod._backup_dir_override = None


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nBAZ=qux\n")
    return str(p)


def test_create_command(runner, env_file):
    result = runner.invoke(backup_cli, ["create", env_file, "--label", "dev"])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_create_command_with_note(runner, env_file):
    result = runner.invoke(backup_cli, ["create", env_file, "--label", "dev", "--note", "pre-release"])
    assert result.exit_code == 0
    assert "pre-release" in result.output


def test_list_command_empty(runner):
    result = runner.invoke(backup_cli, ["list", "--label", "ghost"])
    assert result.exit_code == 0
    assert "No backups" in result.output


def test_list_command_shows_entries(runner, env_file):
    runner.invoke(backup_cli, ["create", env_file, "--label", "dev", "--note", "first"])
    runner.invoke(backup_cli, ["create", env_file, "--label", "dev"])
    result = runner.invoke(backup_cli, ["list", "--label", "dev"])
    assert result.exit_code == 0
    assert "first" in result.output


def test_restore_command(runner, env_file, tmp_path):
    from envoy.backup import create_backup
    entry = create_backup(env_file, label="prod")
    dest = str(tmp_path / "out.env")
    result = runner.invoke(backup_cli, ["restore", "--label", "prod", "--timestamp", entry["timestamp"], dest])
    assert result.exit_code == 0
    assert "Restored" in result.output
    assert os.path.exists(dest)


def test_restore_command_not_found(runner, tmp_path):
    dest = str(tmp_path / "out.env")
    result = runner.invoke(backup_cli, ["restore", "--label", "prod", "--timestamp", "bad-ts", dest])
    assert result.exit_code == 1


def test_delete_command(runner, env_file):
    from envoy.backup import create_backup
    entry = create_backup(env_file, label="ci")
    result = runner.invoke(backup_cli, ["delete", "--label", "ci", "--timestamp", entry["timestamp"]])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_delete_command_not_found(runner):
    result = runner.invoke(backup_cli, ["delete", "--label", "ci", "--timestamp", "bad-ts"])
    assert result.exit_code == 1

"""Tests for envoy/cli_scope.py"""

import pytest
from click.testing import CliRunner
from envoy.cli_scope import scope_cli
import envoy.scope as scope_mod


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def set_scopes_dir(tmp_path):
    original = scope_mod._scopes_dir
    scope_mod._scopes_dir = tmp_path
    yield
    scope_mod._scopes_dir = original


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nAPI_KEY=secret\nPORT=8080\n")
    return str(p)


def test_add_command(runner):
    result = runner.invoke(scope_cli, ["add", "dev", "DB_HOST"])
    assert result.exit_code == 0
    assert "Added" in result.output
    assert "DB_HOST" in scope_mod.get_scope_keys("dev")


def test_add_command_empty_key(runner):
    result = runner.invoke(scope_cli, ["add", "dev", ""])
    assert result.exit_code != 0


def test_remove_command(runner):
    scope_mod.add_key_to_scope("dev", "DB_HOST")
    result = runner.invoke(scope_cli, ["remove", "dev", "DB_HOST"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_command_missing_key(runner):
    result = runner.invoke(scope_cli, ["remove", "dev", "NOPE"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_list_scopes(runner):
    scope_mod.add_key_to_scope("dev", "A")
    scope_mod.add_key_to_scope("prod", "B")
    result = runner.invoke(scope_cli, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_list_keys_in_scope(runner):
    scope_mod.add_key_to_scope("dev", "DB_HOST")
    scope_mod.add_key_to_scope("dev", "PORT")
    result = runner.invoke(scope_cli, ["list", "dev"])
    assert "DB_HOST" in result.output
    assert "PORT" in result.output


def test_list_empty_scopes(runner):
    result = runner.invoke(scope_cli, ["list"])
    assert "No scopes" in result.output


def test_filter_command(runner, env_file):
    scope_mod.add_key_to_scope("backend", "DB_HOST")
    scope_mod.add_key_to_scope("backend", "PORT")
    result = runner.invoke(scope_cli, ["filter", "backend", env_file])
    assert "DB_HOST=localhost" in result.output
    assert "PORT=8080" in result.output
    assert "API_KEY" not in result.output


def test_delete_command(runner):
    scope_mod.add_key_to_scope("tmp", "X")
    result = runner.invoke(scope_cli, ["delete", "tmp"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_missing_scope(runner):
    result = runner.invoke(scope_cli, ["delete", "ghost"])
    assert "not found" in result.output

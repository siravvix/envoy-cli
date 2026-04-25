"""Tests for envoy.cli_transform CLI commands."""

import os
import pytest
from click.testing import CliRunner
from envoy.cli_transform import transform_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    path = tmp_path / ".env"
    path.write_text("db_host=localhost\ndb_port=5432\napp_name=myapp\n")
    return str(path)


def test_uppercase_keys_shows_changes(runner, env_file):
    result = runner.invoke(transform_cli, ["uppercase-keys", env_file])
    assert result.exit_code == 0
    assert "Changes:" in result.output


def test_uppercase_keys_inplace(runner, env_file):
    result = runner.invoke(transform_cli, ["uppercase-keys", env_file, "--inplace"])
    assert result.exit_code == 0
    content = open(env_file).read()
    assert "DB_HOST" in content
    assert "db_host" not in content


def test_uppercase_keys_output_file(runner, env_file, tmp_path):
    out = str(tmp_path / "out.env")
    result = runner.invoke(transform_cli, ["uppercase-keys", env_file, "--output", out])
    assert result.exit_code == 0
    assert os.path.exists(out)
    content = open(out).read()
    assert "DB_HOST" in content


def test_strip_values(runner, tmp_path):
    path = tmp_path / ".env"
    path.write_text("KEY=  hello  \nOTHER=world\n")
    result = runner.invoke(transform_cli, ["strip", str(path), "--inplace"])
    assert result.exit_code == 0
    content = path.read_text()
    assert "hello" in content
    assert "  hello  " not in content


def test_add_prefix_cmd(runner, env_file, tmp_path):
    out = str(tmp_path / "prefixed.env")
    result = runner.invoke(transform_cli, ["add-prefix", env_file, "TEST_", "--output", out])
    assert result.exit_code == 0
    content = open(out).read()
    assert "TEST_db_host" in content or "TEST_DB_HOST" in content


def test_remove_prefix_cmd(runner, tmp_path):
    path = tmp_path / ".env"
    path.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=test\n")
    result = runner.invoke(transform_cli, ["remove-prefix", str(path), "DB_", "--inplace"])
    assert result.exit_code == 0
    content = path.read_text()
    assert "HOST=localhost" in content
    assert "DB_HOST" not in content
    assert "APP_NAME" in content


def test_no_changes_message(runner, env_file):
    # strip on already-clean file should say No changes
    result = runner.invoke(transform_cli, ["strip", env_file])
    assert result.exit_code == 0
    assert "No changes." in result.output

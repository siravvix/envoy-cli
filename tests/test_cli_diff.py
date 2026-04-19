"""Tests for CLI diff commands."""
import os
import pytest
from click.testing import CliRunner
from envoy.cli_diff import diff_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    other = tmp_path / "other.env"
    base.write_text("HOST=localhost\nPORT=5432\nDEBUG=true\n")
    other.write_text("HOST=prod.example.com\nPORT=5432\nSECRET=abc\n")
    return str(base), str(other)


def test_diff_files_shows_changes(runner, env_files):
    base_file, other_file = env_files
    result = runner.invoke(diff_cli, ["files", base_file, other_file])
    assert result.exit_code == 0
    assert "HOST" in result.output


def test_diff_files_added_key(runner, env_files):
    base_file, other_file = env_files
    result = runner.invoke(diff_cli, ["files", base_file, other_file])
    assert "SECRET" in result.output
    assert "+" in result.output


def test_diff_files_removed_key(runner, env_files):
    base_file, other_file = env_files
    result = runner.invoke(diff_cli, ["files", base_file, other_file])
    assert "DEBUG" in result.output
    assert "-" in result.output


def test_diff_files_no_diff(runner, tmp_path):
    env = tmp_path / "same.env"
    env.write_text("KEY=value\n")
    result = runner.invoke(diff_cli, ["files", str(env), str(env)])
    assert result.exit_code == 0
    assert "No differences found." in result.output

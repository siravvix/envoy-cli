"""Tests for envoy.cli_promote CLI commands."""

import os
import pytest
from click.testing import CliRunner
from envoy.cli_promote import promote_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_files(tmp_path):
    src = tmp_path / "source.env"
    tgt = tmp_path / "target.env"
    src.write_text("DB_HOST=prod.db\nDB_PORT=5432\nSECRET=abc\n")
    tgt.write_text("APP_ENV=staging\nDB_HOST=local.db\n")
    return str(src), str(tgt)


def test_promote_files_adds_new_key(runner, env_files):
    src, tgt = env_files
    result = runner.invoke(promote_cli, ["files", src, tgt, "--key", "DB_PORT"])
    assert result.exit_code == 0
    assert "+ DB_PORT" in result.output
    content = open(tgt).read()
    assert "DB_PORT=5432" in content


def test_promote_files_conflict_no_overwrite(runner, env_files):
    src, tgt = env_files
    result = runner.invoke(promote_cli, ["files", src, tgt, "--key", "DB_HOST"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_promote_files_conflict_with_overwrite(runner, env_files):
    src, tgt = env_files
    result = runner.invoke(promote_cli, ["files", src, tgt, "--key", "DB_HOST", "--overwrite"])
    assert result.exit_code == 0
    assert "~ DB_HOST" in result.output


def test_promote_files_dry_run_no_write(runner, env_files):
    src, tgt = env_files
    before = open(tgt).read()
    result = runner.invoke(promote_cli, ["files", src, tgt, "--key", "DB_PORT", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert open(tgt).read() == before


def test_promote_files_missing_key_in_source(runner, env_files):
    src, tgt = env_files
    result = runner.invoke(promote_cli, ["files", src, tgt, "--key", "DOES_NOT_EXIST"])
    assert result.exit_code != 0
    assert "not found in source" in result.output

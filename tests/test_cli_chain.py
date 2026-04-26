"""Tests for envoy.cli_chain commands."""

import pytest
from click.testing import CliRunner
from envoy.cli_chain import chain_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / "base.env"
    base.write_text("APP=myapp\nDEBUG=false\n")

    override = tmp_path / "override.env"
    override.write_text("DEBUG=true\nEXTRA=yes\n")

    return {"base": str(base), "override": str(override), "dir": tmp_path}


def test_show_merged(runner, env_files):
    result = runner.invoke(chain_cli, ["show", env_files["base"], env_files["override"]])
    assert result.exit_code == 0
    assert "DEBUG=true" in result.output
    assert "APP=myapp" in result.output
    assert "EXTRA=yes" in result.output


def test_show_with_source(runner, env_files):
    result = runner.invoke(
        chain_cli, ["show", "--with-source", env_files["base"], env_files["override"]]
    )
    assert result.exit_code == 0
    assert "base.env" in result.output or "override.env" in result.output


def test_show_missing_file(runner, tmp_path):
    result = runner.invoke(chain_cli, ["show", str(tmp_path / "nope.env")])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_conflicts_found(runner, env_files):
    result = runner.invoke(
        chain_cli, ["conflicts", env_files["base"], env_files["override"]]
    )
    assert result.exit_code == 0
    assert "DEBUG" in result.output


def test_conflicts_none(runner, tmp_path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY=same\n")
    b.write_text("KEY=same\n")
    result = runner.invoke(chain_cli, ["conflicts", str(a), str(b)])
    assert result.exit_code == 0
    assert "No conflicts" in result.output


def test_get_key_found(runner, env_files):
    result = runner.invoke(
        chain_cli, ["get", env_files["base"], env_files["override"], "-k", "DEBUG"]
    )
    assert result.exit_code == 0
    assert "true" in result.output


def test_get_key_missing(runner, env_files):
    result = runner.invoke(
        chain_cli, ["get", env_files["base"], "-k", "NONEXISTENT"]
    )
    assert result.exit_code != 0
    assert "not found" in result.output

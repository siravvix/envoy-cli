"""Tests for envoy.cli_inject CLI commands."""

from __future__ import annotations

import sys

import pytest
from click.testing import CliRunner

from envoy.cli_inject import inject_cli


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("HELLO=world\nNUM=42\n")
    return p


# ---------------------------------------------------------------------------
# inject run
# ---------------------------------------------------------------------------

def test_run_command_injects_variable(runner, env_file):
    result = runner.invoke(
        inject_cli,
        [
            "run",
            "--env-file", str(env_file),
            "--no-inherit",
            "--",
            sys.executable, "-c",
            "import os, sys; sys.exit(0 if os.environ.get('HELLO')=='world' else 1)",
        ],
    )
    assert result.exit_code == 0


def test_run_command_missing_env_file(runner, tmp_path):
    result = runner.invoke(
        inject_cli,
        ["run", "--env-file", str(tmp_path / "nope.env"), "--", "echo", "hi"],
    )
    assert result.exit_code != 0


def test_run_command_propagates_exit_code(runner, env_file):
    result = runner.invoke(
        inject_cli,
        [
            "run",
            "--env-file", str(env_file),
            "--",
            sys.executable, "-c", "import sys; sys.exit(7)",
        ],
    )
    assert result.exit_code == 7


# ---------------------------------------------------------------------------
# inject preview
# ---------------------------------------------------------------------------

def test_preview_command_shows_keys(runner, env_file):
    result = runner.invoke(
        inject_cli,
        ["preview", "--env-file", str(env_file)],
    )
    assert result.exit_code == 0
    assert "HELLO=world" in result.output
    assert "NUM=42" in result.output


def test_preview_command_missing_file(runner, tmp_path):
    result = runner.invoke(
        inject_cli,
        ["preview", "--env-file", str(tmp_path / "missing.env")],
    )
    assert result.exit_code != 0
    assert "Error" in result.output or "Error" in (result.output + str(result.exception))

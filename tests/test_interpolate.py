"""Tests for envoy.interpolate and the interpolate CLI."""

import os

import pytest
from click.testing import CliRunner

from envoy.interpolate import (
    InterpolationError,
    find_references,
    interpolate_env,
    interpolate_value,
    unresolved_references,
)
from envoy.cli_interpolate import interpolate_cli


# ---------------------------------------------------------------------------
# interpolate_value
# ---------------------------------------------------------------------------

def test_interpolate_value_curly_braces():
    assert interpolate_value("${FOO}/bar", {"FOO": "hello"}) == "hello/bar"


def test_interpolate_value_dollar_only():
    assert interpolate_value("$FOO/bar", {"FOO": "hello"}) == "hello/bar"


def test_interpolate_value_uses_os_env(monkeypatch):
    monkeypatch.setenv("_TEST_INTERP", "from_os")
    result = interpolate_value("${_TEST_INTERP}", {}, use_os_env=True)
    assert result == "from_os"


def test_interpolate_value_no_os_env_leaves_placeholder(monkeypatch):
    monkeypatch.setenv("_TEST_INTERP", "from_os")
    result = interpolate_value("${_TEST_INTERP}", {}, use_os_env=False)
    assert result == "${_TEST_INTERP}"


def test_interpolate_value_strict_raises():
    with pytest.raises(InterpolationError, match="Unresolved variable"):
        interpolate_value("${MISSING}", {}, use_os_env=False, strict=True)


def test_interpolate_value_no_references():
    assert interpolate_value("plain_value", {}) == "plain_value"


# ---------------------------------------------------------------------------
# interpolate_env
# ---------------------------------------------------------------------------

def test_interpolate_env_chained():
    env = {"BASE": "/app", "DATA": "${BASE}/data", "LOGS": "${DATA}/logs"}
    result = interpolate_env(env, use_os_env=False)
    assert result["DATA"] == "/app/data"
    assert result["LOGS"] == "/app/data/logs"


def test_interpolate_env_does_not_mutate_original():
    env = {"A": "${B}", "B": "hello"}
    interpolate_env(env)
    assert env["A"] == "${B}"  # original unchanged


# ---------------------------------------------------------------------------
# find_references / unresolved_references
# ---------------------------------------------------------------------------

def test_find_references_mixed_syntax():
    refs = find_references("${FOO}/$BAR and ${BAZ}")
    assert refs == ["FOO", "BAR", "BAZ"]


def test_unresolved_references_detects_missing():
    env = {"PATH_VAR": "${BASE}/bin"}
    missing = unresolved_references(env, use_os_env=False)
    assert "PATH_VAR" in missing
    assert "BASE" in missing["PATH_VAR"]


def test_unresolved_references_all_resolved():
    env = {"BASE": "/app", "FULL": "${BASE}/bin"}
    assert unresolved_references(env, use_os_env=False) == {}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_apply_stdout(runner, tmp_path):
    f = tmp_path / ".env"
    f.write_text("BASE=/app\nDATA=${BASE}/data\n")
    result = runner.invoke(interpolate_cli, ["apply", str(f)])
    assert result.exit_code == 0
    assert "DATA=/app/data" in result.output


def test_cli_apply_output_file(runner, tmp_path):
    f = tmp_path / ".env"
    out = tmp_path / "out.env"
    f.write_text("X=hello\nY=${X}_world\n")
    result = runner.invoke(interpolate_cli, ["apply", str(f), "--output", str(out)])
    assert result.exit_code == 0
    assert "Y=hello_world" in out.read_text()


def test_cli_check_no_issues(runner, tmp_path):
    f = tmp_path / ".env"
    f.write_text("A=1\nB=${A}\n")
    result = runner.invoke(interpolate_cli, ["check", str(f)])
    assert result.exit_code == 0
    assert "All references resolved" in result.output


def test_cli_check_reports_missing(runner, tmp_path):
    f = tmp_path / ".env"
    f.write_text("X=${UNDEFINED_VAR}\n")
    result = runner.invoke(interpolate_cli, ["check", str(f), "--no-os-env"])
    assert result.exit_code != 0

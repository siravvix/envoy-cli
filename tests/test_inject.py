"""Tests for envoy.inject module."""

from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest

from envoy.inject import build_env, inject_and_run, preview_env, InjectError


# ---------------------------------------------------------------------------
# build_env
# ---------------------------------------------------------------------------

def test_build_env_merges_overrides():
    base = {"PATH": "/usr/bin", "HOME": "/root"}
    overrides = {"APP_ENV": "test", "HOME": "/override"}
    result = build_env(base, overrides)
    assert result["APP_ENV"] == "test"
    assert result["HOME"] == "/override"  # override wins
    assert result["PATH"] == "/usr/bin"


def test_build_env_empty_base():
    result = build_env({}, {"KEY": "val"})
    assert result == {"KEY": "val"}


def test_build_env_interpolate(tmp_path):
    overrides = {"GREETING": "hello $NAME", "NAME": "world"}
    result = build_env({}, overrides, interpolate=True)
    assert result["GREETING"] == "hello world"


# ---------------------------------------------------------------------------
# inject_and_run
# ---------------------------------------------------------------------------

def test_inject_and_run_no_command_raises(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    with pytest.raises(InjectError, match="No command provided"):
        inject_and_run(str(env_file), [])


def test_inject_and_run_returns_exit_code(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("INJECTED=yes\n")
    code = inject_and_run(
        str(env_file),
        [sys.executable, "-c", "import os, sys; sys.exit(0 if os.environ.get('INJECTED')=='yes' else 1)"],
        inherit_os_env=False,
    )
    assert code == 0


def test_inject_and_run_nonzero_exit(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("X=1\n")
    code = inject_and_run(
        str(env_file),
        [sys.executable, "-c", "import sys; sys.exit(42)"],
    )
    assert code == 42


# ---------------------------------------------------------------------------
# preview_env
# ---------------------------------------------------------------------------

def test_preview_env_returns_dict(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    result = preview_env(str(env_file))
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_preview_env_inherit_includes_os(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("MY_KEY=my_val\n")
    with patch.dict(os.environ, {"OS_KEY": "os_val"}):
        result = preview_env(str(env_file), inherit_os_env=True)
    assert result["MY_KEY"] == "my_val"
    assert result["OS_KEY"] == "os_val"


def test_preview_env_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        preview_env(str(tmp_path / "nonexistent.env"))

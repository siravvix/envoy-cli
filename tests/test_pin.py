"""Tests for envoy.pin and envoy.cli_pin."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envoy.pin import pin_key, unpin_key, is_pinned, list_pinned, filter_protected
from envoy.cli_pin import pin_cli


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY1=val1\nKEY2=val2\n")
    return str(f)


@pytest.fixture
def runner():
    return CliRunner()


def test_pin_and_is_pinned(env_file):
    assert not is_pinned(env_file, "KEY1")
    pin_key(env_file, "KEY1")
    assert is_pinned(env_file, "KEY1")


def test_pin_with_reason(env_file):
    pin_key(env_file, "KEY1", reason="do not touch")
    from envoy.pin import load_pins
    pins = load_pins(env_file)
    assert pins["KEY1"]["reason"] == "do not touch"


def test_unpin_existing(env_file):
    pin_key(env_file, "KEY1")
    result = unpin_key(env_file, "KEY1")
    assert result is True
    assert not is_pinned(env_file, "KEY1")


def test_unpin_nonexistent(env_file):
    result = unpin_key(env_file, "MISSING")
    assert result is False


def test_list_pinned_sorted(env_file):
    pin_key(env_file, "ZEBRA")
    pin_key(env_file, "ALPHA")
    assert list_pinned(env_file) == ["ALPHA", "ZEBRA"]


def test_filter_protected_removes_pinned(env_file):
    pin_key(env_file, "KEY1")
    updates = {"KEY1": "new1", "KEY2": "new2"}
    safe = filter_protected(env_file, updates)
    assert "KEY1" not in safe
    assert safe["KEY2"] == "new2"


def test_cli_add_and_list(runner, env_file):
    result = runner.invoke(pin_cli, ["add", env_file, "KEY1", "--reason", "stable"])
    assert result.exit_code == 0
    assert "Pinned 'KEY1'" in result.output

    result = runner.invoke(pin_cli, ["list", env_file])
    assert result.exit_code == 0
    assert "KEY1" in result.output
    assert "stable" in result.output


def test_cli_remove(runner, env_file):
    runner.invoke(pin_cli, ["add", env_file, "KEY2"])
    result = runner.invoke(pin_cli, ["remove", env_file, "KEY2"])
    assert result.exit_code == 0
    assert "Unpinned" in result.output


def test_cli_remove_not_pinned(runner, env_file):
    result = runner.invoke(pin_cli, ["remove", env_file, "NOPE"])
    assert result.exit_code != 0


def test_cli_list_empty(runner, env_file):
    result = runner.invoke(pin_cli, ["list", env_file])
    assert result.exit_code == 0
    assert "No keys are pinned" in result.output

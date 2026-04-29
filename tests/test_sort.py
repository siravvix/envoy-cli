"""Tests for envoy.sort and envoy.cli_sort."""

import pytest
from click.testing import CliRunner

from envoy.sort import (
    sort_keys,
    sort_by_value,
    group_and_sort,
    move_key,
    custom_order,
    format_sort_summary,
)
from envoy.cli_sort import sort_cli


# ── unit tests ────────────────────────────────────────────────────────────────

def test_sort_keys_basic():
    env = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort_keys(env)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_keys_reverse():
    env = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort_keys(env, reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_keys_does_not_mutate():
    env = {"B": "1", "A": "2"}
    sort_keys(env)
    assert list(env.keys()) == ["B", "A"]


def test_sort_by_value_basic():
    env = {"KEY_B": "banana", "KEY_A": "apple", "KEY_C": "cherry"}
    result = sort_by_value(env)
    assert list(result.keys()) == ["KEY_A", "KEY_B", "KEY_C"]


def test_group_and_sort_basic():
    env = {"DB_HOST": "1", "APP_NAME": "2", "DB_PORT": "3", "APP_ENV": "4"}
    result = group_and_sort(env)
    keys = list(result.keys())
    # APP_ group should precede DB_ group
    assert keys.index("APP_ENV") < keys.index("DB_HOST")
    assert keys.index("APP_NAME") < keys.index("DB_HOST")


def test_move_key_to_front():
    env = {"A": "1", "B": "2", "C": "3"}
    result = move_key(env, "C", 0)
    assert list(result.keys()) == ["C", "A", "B"]


def test_move_key_to_end():
    env = {"A": "1", "B": "2", "C": "3"}
    result = move_key(env, "A", 2)
    assert list(result.keys()) == ["B", "C", "A"]


def test_move_key_missing_raises():
    env = {"A": "1"}
    with pytest.raises(KeyError):
        move_key(env, "Z", 0)


def test_custom_order_basic():
    env = {"C": "3", "A": "1", "B": "2"}
    result = custom_order(env, ["A", "B"])
    keys = list(result.keys())
    assert keys[0] == "A"
    assert keys[1] == "B"
    assert keys[2] == "C"


def test_custom_order_missing_key_ignored():
    env = {"A": "1", "B": "2"}
    result = custom_order(env, ["Z", "A"])
    assert list(result.keys())[0] == "A"


def test_format_sort_summary_with_changes():
    original = {"B": "2", "A": "1"}
    sorted_env = sort_keys(original)
    summary = format_sort_summary(original, sorted_env)
    assert "Key order changes:" in summary
    assert "A" in summary


def test_format_sort_summary_no_changes():
    env = {"A": "1", "B": "2"}
    summary = format_sort_summary(env, env)
    assert "no changes" in summary


# ── CLI tests ─────────────────────────────────────────────────────────────────

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("ZEBRA=1\nAPPLE=2\nMANGO=3\n")
    return str(f)


def test_cli_sort_keys_shows_summary(runner, env_file):
    result = runner.invoke(sort_cli, ["keys", env_file])
    assert result.exit_code == 0
    assert "Key order changes:" in result.output


def test_cli_sort_keys_inplace(runner, env_file):
    result = runner.invoke(sort_cli, ["keys", env_file, "--inplace"])
    assert result.exit_code == 0
    content = open(env_file).read()
    lines = [l.split("=")[0] for l in content.strip().splitlines()]
    assert lines == sorted(lines)


def test_cli_move_key(runner, env_file):
    result = runner.invoke(sort_cli, ["move", env_file, "MANGO", "0"])
    assert result.exit_code == 0
    assert "Key order changes:" in result.output


def test_cli_move_missing_key(runner, env_file):
    result = runner.invoke(sort_cli, ["move", env_file, "NOPE", "0"])
    assert result.exit_code != 0
    assert "Error" in result.output

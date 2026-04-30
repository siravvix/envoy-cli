"""Tests for envoy.fmt formatting module."""

import pytest
from envoy.fmt import (
    sort_keys_alpha,
    align_values,
    normalize_quotes,
    remove_blank_lines,
    format_env,
)


def test_sort_keys_alpha_basic():
    env = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort_keys_alpha(env)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_keys_alpha_does_not_mutate():
    env = {"B": "2", "A": "1"}
    original_order = list(env.keys())
    sort_keys_alpha(env)
    assert list(env.keys()) == original_order


def test_align_values_pads_shorter_keys():
    env = {"A": "1", "LONG_KEY": "2"}
    lines = align_values(env)
    assert lines[0] == "A       =1"
    assert lines[1] == "LONG_KEY=2"


def test_align_values_empty():
    assert align_values({}) == []


def test_normalize_quotes_plain_value():
    assert normalize_quotes("hello") == "hello"


def test_normalize_quotes_value_with_space():
    result = normalize_quotes("hello world")
    assert result == '"hello world"'


def test_normalize_quotes_already_quoted():
    result = normalize_quotes('"already quoted"')
    assert result == '"already quoted"'


def test_normalize_quotes_with_hash():
    result = normalize_quotes("val#ue")
    assert result.startswith('"')


def test_remove_blank_lines_collapses_doubles():
    lines = ["A=1", "", "", "B=2"]
    result = remove_blank_lines(lines)
    assert result == ["A=1", "", "B=2"]


def test_remove_blank_lines_single_blank_kept():
    lines = ["A=1", "", "B=2"]
    assert remove_blank_lines(lines) == ["A=1", "", "B=2"]


def test_format_env_basic():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = format_env(env)
    assert "FOO=bar" in result
    assert "BAZ=qux" in result


def test_format_env_sort():
    env = {"Z": "1", "A": "2"}
    result = format_env(env, sort=True)
    lines = result.strip().splitlines()
    assert lines[0].startswith("A")
    assert lines[1].startswith("Z")


def test_format_env_ends_with_newline():
    env = {"K": "V"}
    assert format_env(env).endswith("\n")


def test_format_env_empty():
    assert format_env({}) == ""

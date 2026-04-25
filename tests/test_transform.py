"""Tests for envoy.transform module."""

import pytest
from envoy.transform import (
    uppercase_keys,
    lowercase_values,
    strip_values,
    add_prefix,
    remove_prefix,
    apply_transform,
    format_transform_summary,
)


def test_uppercase_keys_basic():
    env = {"db_host": "localhost", "app_port": "8080"}
    result = uppercase_keys(env)
    assert result == {"DB_HOST": "localhost", "APP_PORT": "8080"}


def test_uppercase_keys_does_not_mutate():
    env = {"key": "val"}
    uppercase_keys(env)
    assert "key" in env


def test_lowercase_values():
    env = {"HOST": "LOCALHOST", "ENV": "PRODUCTION"}
    result = lowercase_values(env)
    assert result == {"HOST": "localhost", "ENV": "production"}


def test_strip_values():
    env = {"KEY": "  hello  ", "OTHER": "\tworld\n"}
    result = strip_values(env)
    assert result == {"KEY": "hello", "OTHER": "world"}


def test_add_prefix():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = add_prefix(env, "DB_")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_remove_prefix_matching_keys():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
    result = remove_prefix(env, "DB_")
    assert result == {"HOST": "localhost", "PORT": "5432", "APP_NAME": "myapp"}


def test_remove_prefix_no_match():
    env = {"APP_NAME": "test"}
    result = remove_prefix(env, "DB_")
    assert result == {"APP_NAME": "test"}


def test_apply_transform_values():
    env = {"KEY": "hello"}
    result = apply_transform(env, str.upper, target="values")
    assert result == {"KEY": "HELLO"}


def test_apply_transform_keys():
    env = {"key": "val"}
    result = apply_transform(env, str.upper, target="keys")
    assert result == {"KEY": "val"}


def test_apply_transform_invalid_target():
    with pytest.raises(ValueError, match="target must be"):
        apply_transform({}, str.upper, target="both")


def test_format_transform_summary_changed():
    original = {"KEY": "old"}
    transformed = {"KEY": "new"}
    lines = format_transform_summary(original, transformed)
    assert any("KEY" in l and "old" in l and "new" in l for l in lines)


def test_format_transform_summary_added():
    original = {}
    transformed = {"NEW_KEY": "val"}
    lines = format_transform_summary(original, transformed)
    assert any(l.startswith("  +") and "NEW_KEY" in l for l in lines)


def test_format_transform_summary_removed():
    original = {"OLD_KEY": "val"}
    transformed = {}
    lines = format_transform_summary(original, transformed)
    assert any(l.startswith("  -") and "OLD_KEY" in l for l in lines)


def test_format_transform_summary_no_changes():
    env = {"KEY": "val"}
    lines = format_transform_summary(env, env.copy())
    assert lines == []

"""Tests for envoy.diff module."""
import pytest
from envoy.diff import diff_envs, format_diff, has_diff


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
OTHER = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


def test_diff_added():
    result = diff_envs(BASE, OTHER)
    added_keys = [k for k, _, _ in result["added"]]
    assert "SECRET" in added_keys


def test_diff_removed():
    result = diff_envs(BASE, OTHER)
    removed_keys = [k for k, _, _ in result["removed"]]
    assert "DEBUG" in removed_keys


def test_diff_changed():
    result = diff_envs(BASE, OTHER)
    changed_keys = [k for k, _, _ in result["changed"]]
    assert "HOST" in changed_keys


def test_diff_unchanged_key_not_in_changed():
    result = diff_envs(BASE, OTHER)
    changed_keys = [k for k, _, _ in result["changed"]]
    assert "PORT" not in changed_keys


def test_has_diff_true():
    result = diff_envs(BASE, OTHER)
    assert has_diff(result) is True


def test_has_diff_false():
    result = diff_envs(BASE, BASE)
    assert has_diff(result) is False


def test_format_diff_no_differences():
    result = diff_envs(BASE, BASE)
    assert format_diff(result) == "No differences found."


def test_format_diff_contains_symbols():
    result = diff_envs(BASE, OTHER)
    output = format_diff(result)
    assert "+" in output or "-" in output or "~" in output

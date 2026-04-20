"""Tests for envoy.snapshot module."""
import pytest
from envoy.snapshot import (
    compare_snapshots,
    summarize_snapshot,
    format_snapshot_diff,
    snapshot_changelog,
)


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "NEW_KEY": "hello"}


def test_compare_snapshots_detects_changes():
    result = compare_snapshots(ENV_A, ENV_B)
    assert result["has_changes"] is True
    assert "HOST" in result["changed"]
    assert "NEW_KEY" in result["added"]
    assert "DEBUG" in result["removed"]
    assert "PORT" in result["unchanged"]


def test_compare_snapshots_no_changes():
    result = compare_snapshots(ENV_A, ENV_A)
    assert result["has_changes"] is False
    assert not result["added"]
    assert not result["removed"]
    assert not result["changed"]


def test_summarize_snapshot_basic():
    env = {"A": "1", "B": "", "C": "value"}
    summary = summarize_snapshot(env)
    assert summary["total_keys"] == 3
    assert "B" in summary["empty_values"]
    assert summary["keys"] == ["A", "B", "C"]


def test_summarize_snapshot_no_empty():
    env = {"X": "1", "Y": "2"}
    summary = summarize_snapshot(env)
    assert summary["empty_values"] == []


def test_format_snapshot_diff_with_changes():
    output = format_snapshot_diff(ENV_A, ENV_B)
    assert "HOST" in output
    assert "NEW_KEY" in output
    assert "DEBUG" in output


def test_format_snapshot_diff_no_changes():
    output = format_snapshot_diff(ENV_A, ENV_A)
    assert output == "No changes between snapshots."


def test_snapshot_changelog():
    env_c = {"HOST": "prod.example.com", "PORT": "5433"}
    snapshots = [("v1", ENV_A), ("v2", ENV_B), ("v3", env_c)]
    changelog = snapshot_changelog(snapshots)
    assert len(changelog) == 2
    assert changelog[0]["from"] == "v1"
    assert changelog[0]["to"] == "v2"
    assert changelog[1]["from"] == "v2"
    assert changelog[1]["to"] == "v3"
    assert changelog[1]["has_changes"] is True


def test_snapshot_changelog_single():
    changelog = snapshot_changelog([("v1", ENV_A)])
    assert changelog == []

"""Tests for envoy.merge and cli_merge."""

import pytest
from click.testing import CliRunner
from envoy.merge import merge_envs, merge_summary, STRATEGY_OURS, STRATEGY_THEIRS
from envoy.cli_merge import merge_cli


def test_merge_adds_new_keys():
    base = {"A": "1"}
    other = {"B": "2"}
    result = merge_envs(base, other)
    assert result == {"A": "1", "B": "2"}


def test_merge_ours_keeps_base_on_conflict():
    base = {"A": "1"}
    other = {"A": "99"}
    result = merge_envs(base, other, strategy=STRATEGY_OURS)
    assert result["A"] == "1"


def test_merge_theirs_overrides_on_conflict():
    base = {"A": "1"}
    other = {"A": "99"}
    result = merge_envs(base, other, strategy=STRATEGY_THEIRS)
    assert result["A"] == "99"


def test_merge_no_conflict():
    base = {"A": "1", "B": "2"}
    other = {"B": "2", "C": "3"}
    result = merge_envs(base, other)
    assert result == {"A": "1", "B": "2", "C": "3"}


def test_merge_summary_added():
    base = {"A": "1"}
    other = {"B": "2"}
    merged = merge_envs(base, other)
    summary = merge_summary(base, other, merged)
    assert "B" in summary["added"]
    assert summary["overridden"] == []
    assert summary["kept"] == []


def test_merge_summary_kept_and_overridden():
    base = {"A": "1", "B": "old"}
    other = {"A": "new", "B": "new"}
    merged_ours = merge_envs(base, other, strategy=STRATEGY_OURS)
    summary = merge_summary(base, other, merged_ours)
    assert "A" in summary["kept"]
    assert "B" in summary["kept"]

    merged_theirs = merge_envs(base, other, strategy=STRATEGY_THEIRS)
    summary2 = merge_summary(base, other, merged_theirs)
    assert "A" in summary2["overridden"]


def test_cli_merge_files(tmp_path):
    base = tmp_path / ".env.base"
    other = tmp_path / ".env.other"
    out = tmp_path / ".env.out"
    base.write_text("A=1\nB=old\n")
    other.write_text("B=new\nC=3\n")

    runner = CliRunner()
    result = runner.invoke(
        merge_cli,
        ["files", str(base), str(other), "--output", str(out), "--strategy", "theirs"],
    )
    assert result.exit_code == 0
    content = out.read_text()
    assert "B=new" in content
    assert "C=3" in content
    assert "A=1" in content

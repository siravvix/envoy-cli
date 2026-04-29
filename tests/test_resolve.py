"""Tests for envoy.resolve module."""

import pytest
from envoy.resolve import (
    resolve_key,
    resolve_all,
    resolve_missing,
    resolve_sources_for_key,
    resolve_files,
    format_resolve_trace,
    ResolveError,
)


SOURCE_A = {"DB_HOST": "localhost", "DB_PORT": "5432"}
SOURCE_B = {"DB_HOST": "prod.db", "API_KEY": "abc123"}


def test_resolve_key_last_source_wins():
    result = resolve_key("DB_HOST", [SOURCE_A, SOURCE_B])
    assert result == "prod.db"


def test_resolve_key_only_in_first():
    result = resolve_key("DB_PORT", [SOURCE_A, SOURCE_B])
    assert result == "5432"


def test_resolve_key_not_found_returns_none():
    result = resolve_key("MISSING", [SOURCE_A, SOURCE_B])
    assert result is None


def test_resolve_all_merges_sources():
    merged = resolve_all([SOURCE_A, SOURCE_B])
    assert merged["DB_HOST"] == "prod.db"
    assert merged["DB_PORT"] == "5432"
    assert merged["API_KEY"] == "abc123"


def test_resolve_all_empty_sources():
    assert resolve_all([]) == {}


def test_resolve_missing_finds_absent_keys():
    absent = resolve_missing(["DB_HOST", "SECRET", "DB_PORT"], [SOURCE_A])
    assert absent == ["SECRET"]


def test_resolve_missing_all_present():
    absent = resolve_missing(["DB_HOST"], [SOURCE_A, SOURCE_B])
    assert absent == []


def test_resolve_sources_for_key_lists_all():
    hits = resolve_sources_for_key("DB_HOST", [("a", SOURCE_A), ("b", SOURCE_B)])
    assert hits == [("a", "localhost"), ("b", "prod.db")]


def test_resolve_sources_for_key_not_found():
    hits = resolve_sources_for_key("NOPE", [("a", SOURCE_A)])
    assert hits == []


def test_resolve_files_last_wins(tmp_path):
    f1 = tmp_path / "a.env"
    f1.write_text("DB_HOST=localhost\n")
    f2 = tmp_path / "b.env"
    f2.write_text("DB_HOST=prod\n")
    assert resolve_files("DB_HOST", [str(f1), str(f2)]) == "prod"


def test_resolve_files_missing_file_raises(tmp_path):
    with pytest.raises(ResolveError, match="File not found"):
        resolve_files("X", ["/nonexistent/path.env"])


def test_format_resolve_trace_shows_winner():
    named = [("base", SOURCE_A), ("prod", SOURCE_B)]
    output = format_resolve_trace("DB_HOST", named)
    assert "localhost" in output
    assert "prod.db" in output
    assert "active" in output


def test_format_resolve_trace_not_found():
    named = [("base", SOURCE_A)]
    output = format_resolve_trace("MISSING", named)
    assert "not found" in output

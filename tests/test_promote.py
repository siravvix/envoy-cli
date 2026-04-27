"""Tests for envoy.promote module."""

import pytest
from envoy.promote import promote_keys, promote_summary, PromoteError


SOURCE = {"DB_HOST": "prod.db", "DB_PORT": "5432", "SECRET": "abc123"}
TARGET = {"DB_HOST": "local.db", "APP_ENV": "staging"}


def test_promote_all_keys_no_conflict():
    result = promote_keys({"NEW_KEY": "val"}, TARGET)
    assert result["NEW_KEY"] == "val"
    assert result["APP_ENV"] == "staging"


def test_promote_specific_keys():
    result = promote_keys(SOURCE, TARGET, keys=["DB_PORT"])
    assert result["DB_PORT"] == "5432"
    assert "SECRET" not in result


def test_promote_missing_key_raises():
    with pytest.raises(PromoteError, match="not found in source"):
        promote_keys(SOURCE, TARGET, keys=["NONEXISTENT"])


def test_promote_conflict_no_overwrite_raises():
    with pytest.raises(PromoteError, match="already exists"):
        promote_keys(SOURCE, TARGET, keys=["DB_HOST"], overwrite=False)


def test_promote_conflict_with_overwrite():
    result = promote_keys(SOURCE, TARGET, keys=["DB_HOST"], overwrite=True)
    assert result["DB_HOST"] == "prod.db"


def test_promote_does_not_mutate_target():
    original_target = dict(TARGET)
    promote_keys({"NEW": "x"}, TARGET)
    assert TARGET == original_target


def test_promote_summary_added():
    result = promote_keys({"NEW": "v"}, TARGET)
    summary = promote_summary(SOURCE, TARGET, result)
    assert "NEW" in summary["added"]


def test_promote_summary_updated():
    result = promote_keys(SOURCE, TARGET, keys=["DB_HOST"], overwrite=True)
    summary = promote_summary(SOURCE, TARGET, result)
    assert "DB_HOST" in summary["updated"]


def test_promote_summary_unchanged():
    merged = dict(TARGET)
    summary = promote_summary(SOURCE, TARGET, merged)
    assert set(summary["unchanged"]) == set(TARGET.keys())
    assert summary["added"] == []
    assert summary["updated"] == []


def test_promote_all_keys_from_source():
    result = promote_keys(SOURCE, {}, overwrite=False)
    assert result == SOURCE

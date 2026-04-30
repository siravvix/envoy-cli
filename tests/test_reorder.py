"""Tests for envoy.reorder module."""
import pytest
from envoy.reorder import (
    reorder_by_list,
    reorder_by_prefix_priority,
    move_to_top,
    move_to_bottom,
    format_reorder_diff,
    ReorderError,
)


SAMPLE = {"DB_HOST": "localhost", "APP_NAME": "myapp", "DB_PORT": "5432", "APP_ENV": "prod", "SECRET": "abc"}


def test_reorder_by_list_basic():
    order = ["APP_NAME", "APP_ENV", "DB_HOST", "DB_PORT", "SECRET"]
    result = reorder_by_list(SAMPLE, order)
    assert list(result.keys()) == order


def test_reorder_by_list_partial_order_appends_remaining():
    result = reorder_by_list(SAMPLE, ["SECRET", "APP_NAME"])
    keys = list(result.keys())
    assert keys[0] == "SECRET"
    assert keys[1] == "APP_NAME"
    assert set(keys) == set(SAMPLE.keys())


def test_reorder_by_list_no_append_omits_extras():
    result = reorder_by_list(SAMPLE, ["SECRET", "APP_NAME"], append_remaining=False)
    assert list(result.keys()) == ["SECRET", "APP_NAME"]


def test_reorder_by_list_unknown_key_skipped():
    result = reorder_by_list(SAMPLE, ["MISSING_KEY", "APP_NAME"])
    assert "MISSING_KEY" not in result
    assert "APP_NAME" in result


def test_reorder_by_prefix_priority_basic():
    result = reorder_by_prefix_priority(SAMPLE, ["APP", "DB"])
    keys = list(result.keys())
    app_indices = [keys.index(k) for k in keys if k.startswith("APP_")]
    db_indices = [keys.index(k) for k in keys if k.startswith("DB_")]
    assert max(app_indices) < min(db_indices)


def test_reorder_by_prefix_priority_remaining_at_end():
    result = reorder_by_prefix_priority(SAMPLE, ["APP", "DB"])
    keys = list(result.keys())
    assert keys[-1] == "SECRET"


def test_move_to_top_basic():
    result = move_to_top(SAMPLE, ["SECRET", "DB_PORT"])
    keys = list(result.keys())
    assert keys[0] == "SECRET"
    assert keys[1] == "DB_PORT"
    assert len(result) == len(SAMPLE)


def test_move_to_top_missing_key_raises():
    with pytest.raises(ReorderError, match="MISSING"):
        move_to_top(SAMPLE, ["MISSING"])


def test_move_to_bottom_basic():
    result = move_to_bottom(SAMPLE, ["DB_HOST", "APP_NAME"])
    keys = list(result.keys())
    assert keys[-2] == "DB_HOST"
    assert keys[-1] == "APP_NAME"
    assert len(result) == len(SAMPLE)


def test_move_to_bottom_missing_key_raises():
    with pytest.raises(ReorderError, match="NOPE"):
        move_to_bottom(SAMPLE, ["NOPE"])


def test_format_reorder_diff_shows_changes():
    reordered = move_to_top(SAMPLE, ["SECRET"])
    diff = format_reorder_diff(SAMPLE, reordered)
    assert "SECRET" in diff
    assert "->" in diff


def test_format_reorder_diff_no_change():
    diff = format_reorder_diff(SAMPLE, dict(SAMPLE))
    assert "no position changes" in diff


def test_reorder_does_not_mutate_original():
    original = dict(SAMPLE)
    reorder_by_list(SAMPLE, ["SECRET"])
    assert list(SAMPLE.keys()) == list(original.keys())

import os
import pytest
from pathlib import Path
from envoy.history import (
    record_snapshot, read_history, clear_history, get_snapshot,
    HISTORY_DIR_ENV
)


@pytest.fixture(autouse=True)
def set_history_dir(tmp_path, monkeypatch):
    monkeypatch.setenv(HISTORY_DIR_ENV, str(tmp_path / "history"))


def test_read_history_empty():
    assert read_history("dev") == []


def test_record_and_read_single():
    record_snapshot("dev", {"KEY": "value"}, message="initial")
    entries = read_history("dev")
    assert len(entries) == 1
    assert entries[0]["env"] == {"KEY": "value"}
    assert entries[0]["message"] == "initial"
    assert "timestamp" in entries[0]


def test_multiple_snapshots_order():
    record_snapshot("dev", {"A": "1"}, message="first")
    record_snapshot("dev", {"A": "2"}, message="second")
    entries = read_history("dev")
    assert len(entries) == 2
    assert entries[0]["message"] == "first"
    assert entries[1]["message"] == "second"


def test_get_snapshot_valid():
    record_snapshot("prod", {"X": "10"})
    snap = get_snapshot("prod", 0)
    assert snap is not None
    assert snap["env"] == {"X": "10"}


def test_get_snapshot_out_of_range():
    record_snapshot("prod", {"X": "10"})
    assert get_snapshot("prod", 5) is None


def test_get_snapshot_no_history():
    assert get_snapshot("ghost", 0) is None


def test_clear_history():
    record_snapshot("dev", {"K": "v"})
    clear_history("dev")
    assert read_history("dev") == []


def test_clear_nonexistent_profile():
    clear_history("nonexistent")  # should not raise


def test_profiles_isolated():
    record_snapshot("dev", {"A": "1"})
    record_snapshot("prod", {"B": "2"})
    assert len(read_history("dev")) == 1
    assert len(read_history("prod")) == 1

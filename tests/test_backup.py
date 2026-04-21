"""Tests for envoy.backup module."""

import os
import pytest
import tempfile
from datetime import datetime, timezone

import envoy.backup as backup_mod
from envoy.backup import create_backup, list_backups, restore_backup, delete_backup


@pytest.fixture(autouse=True)
def set_backup_dir(tmp_path):
    backup_mod._backup_dir_override = str(tmp_path / "backups")
    yield
    backup_mod._backup_dir_override = None


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("API_KEY=secret\nDEBUG=true\n")
    return str(p)


def test_create_backup_returns_entry(env_file):
    entry = create_backup(env_file, label="dev")
    assert "timestamp" in entry
    assert os.path.exists(entry["file"])
    assert entry["note"] == ""


def test_create_backup_with_note(env_file):
    entry = create_backup(env_file, label="dev", note="before deploy")
    assert entry["note"] == "before deploy"


def test_create_backup_missing_source():
    with pytest.raises(FileNotFoundError):
        create_backup("/nonexistent/.env", label="dev")


def test_list_backups_empty():
    result = list_backups("nonexistent")
    assert result == []


def test_list_backups_newest_first(env_file):
    e1 = create_backup(env_file, label="staging")
    e2 = create_backup(env_file, label="staging")
    entries = list_backups("staging")
    assert len(entries) == 2
    assert entries[0]["timestamp"] == e2["timestamp"]
    assert entries[1]["timestamp"] == e1["timestamp"]


def test_restore_backup(env_file, tmp_path):
    entry = create_backup(env_file, label="prod")
    dest = str(tmp_path / "restored.env")
    restore_backup("prod", entry["timestamp"], dest)
    assert os.path.exists(dest)
    content = open(dest).read()
    assert "API_KEY=secret" in content


def test_restore_backup_not_found():
    with pytest.raises(KeyError):
        restore_backup("prod", "2099-01-01T00:00:00Z", "/tmp/out.env")


def test_delete_backup(env_file):
    entry = create_backup(env_file, label="ci")
    delete_backup("ci", entry["timestamp"])
    assert list_backups("ci") == []
    assert not os.path.exists(entry["file"])


def test_delete_backup_not_found():
    with pytest.raises(KeyError):
        delete_backup("ci", "2099-01-01T00:00:00Z")

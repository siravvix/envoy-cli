"""Backup and restore .env file snapshots to a local backup store."""

import os
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BACKUP_DIR = os.path.join(os.path.expanduser("~"), ".envoy", "backups")
_backup_dir_override = None


def get_backup_dir() -> str:
    return _backup_dir_override or DEFAULT_BACKUP_DIR


def _backup_index_path(label: str) -> str:
    return os.path.join(get_backup_dir(), label, "index.json")


def _load_index(label: str) -> list:
    path = _backup_index_path(label)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def _save_index(label: str, index: list) -> None:
    path = _backup_index_path(label)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f, indent=2)


def create_backup(source_path: str, label: str, note: str = "") -> dict:
    """Copy source_path into the backup store under label."""
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file not found: {source_path}")
    ts = datetime.now(timezone.utc).isoformat()
    safe_ts = ts.replace(":", "-").replace("+", "Z")
    backup_dir = os.path.join(get_backup_dir(), label)
    os.makedirs(backup_dir, exist_ok=True)
    dest = os.path.join(backup_dir, f"{safe_ts}.env")
    shutil.copy2(source_path, dest)
    entry = {"timestamp": ts, "file": dest, "note": note}
    index = _load_index(label)
    index.append(entry)
    _save_index(label, index)
    return entry


def list_backups(label: str) -> list:
    """Return all backup entries for a label, newest first."""
    index = _load_index(label)
    return list(reversed(index))


def restore_backup(label: str, timestamp: str, dest_path: str) -> None:
    """Restore a backup identified by timestamp to dest_path."""
    index = _load_index(label)
    match = next((e for e in index if e["timestamp"] == timestamp), None)
    if match is None:
        raise KeyError(f"No backup found for label={label!r} at {timestamp}")
    shutil.copy2(match["file"], dest_path)


def delete_backup(label: str, timestamp: str) -> None:
    """Remove a specific backup entry and its file."""
    index = _load_index(label)
    match = next((e for e in index if e["timestamp"] == timestamp), None)
    if match is None:
        raise KeyError(f"No backup found for label={label!r} at {timestamp}")
    if os.path.exists(match["file"]):
        os.remove(match["file"])
    index = [e for e in index if e["timestamp"] != timestamp]
    _save_index(label, index)

"""Freeze and unfreeze .env files to prevent accidental modification."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

_FREEZE_INDEX_NAME = ".envoy_frozen"


def get_freeze_index_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.home() / ".envoy"
    base.mkdir(parents=True, exist_ok=True)
    return base / _FREEZE_INDEX_NAME


def _load_index(index_path: Path) -> dict:
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    return {}


def _save_index(index_path: Path, data: dict) -> None:
    with open(index_path, "w") as f:
        json.dump(data, f, indent=2)


def freeze_file(filepath: str, directory: Optional[str] = None) -> None:
    """Mark a file as frozen."""
    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    index_path = get_freeze_index_path(directory)
    index = _load_index(index_path)
    index[str(path)] = {"frozen": True}
    _save_index(index_path, index)


def unfreeze_file(filepath: str, directory: Optional[str] = None) -> bool:
    """Unmark a file as frozen. Returns True if it was frozen."""
    path = Path(filepath).resolve()
    index_path = get_freeze_index_path(directory)
    index = _load_index(index_path)
    key = str(path)
    if key in index:
        del index[key]
        _save_index(index_path, index)
        return True
    return False


def is_frozen(filepath: str, directory: Optional[str] = None) -> bool:
    """Return True if the file is frozen."""
    path = Path(filepath).resolve()
    index_path = get_freeze_index_path(directory)
    index = _load_index(index_path)
    return str(path) in index


def list_frozen(directory: Optional[str] = None) -> list[str]:
    """Return all currently frozen file paths."""
    index_path = get_freeze_index_path(directory)
    index = _load_index(index_path)
    return list(index.keys())


def assert_not_frozen(filepath: str, directory: Optional[str] = None) -> None:
    """Raise an error if the file is frozen."""
    if is_frozen(filepath, directory):
        raise PermissionError(f"File is frozen and cannot be modified: {filepath}")

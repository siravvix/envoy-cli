"""Alias management: create short names for env keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_ALIASES_FILENAME = "aliases.json"


def get_aliases_path(base_dir: Optional[Path] = None) -> Path:
    if base_dir is None:
        base_dir = Path.home() / ".envoy"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / _ALIASES_FILENAME


def load_aliases(base_dir: Optional[Path] = None) -> Dict[str, str]:
    path = get_aliases_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_aliases(aliases: Dict[str, str], base_dir: Optional[Path] = None) -> None:
    path = get_aliases_path(base_dir)
    path.write_text(json.dumps(aliases, indent=2))


def add_alias(alias: str, key: str, base_dir: Optional[Path] = None) -> None:
    """Map *alias* -> *key*."""
    if not alias or not key:
        raise ValueError("alias and key must be non-empty strings")
    aliases = load_aliases(base_dir)
    aliases[alias] = key
    save_aliases(aliases, base_dir)


def remove_alias(alias: str, base_dir: Optional[Path] = None) -> None:
    aliases = load_aliases(base_dir)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found")
    del aliases[alias]
    save_aliases(aliases, base_dir)


def resolve_alias(alias: str, base_dir: Optional[Path] = None) -> Optional[str]:
    """Return the key that *alias* maps to, or None."""
    return load_aliases(base_dir).get(alias)


def list_aliases(base_dir: Optional[Path] = None) -> Dict[str, str]:
    return load_aliases(base_dir)


def format_aliases(aliases: Dict[str, str]) -> str:
    if not aliases:
        return "(no aliases defined)"
    width = max(len(a) for a in aliases)
    return "\n".join(f"{a:<{width}}  ->  {k}" for a, k in sorted(aliases.items()))

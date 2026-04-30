"""Deprecation tracking for .env keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.profiles import get_profiles_dir


def get_deprecations_path(profile: str = "default") -> Path:
    return get_profiles_dir() / profile / "deprecations.json"


def load_deprecations(profile: str = "default") -> Dict[str, dict]:
    path = get_deprecations_path(profile)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_deprecations(data: Dict[str, dict], profile: str = "default") -> None:
    path = get_deprecations_path(profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def deprecate_key(
    key: str,
    reason: str = "",
    replacement: Optional[str] = None,
    profile: str = "default",
) -> None:
    if not key:
        raise ValueError("Key must not be empty.")
    data = load_deprecations(profile)
    data[key] = {"reason": reason, "replacement": replacement}
    save_deprecations(data, profile)


def undeprecate_key(key: str, profile: str = "default") -> bool:
    data = load_deprecations(profile)
    if key not in data:
        return False
    del data[key]
    save_deprecations(data, profile)
    return True


def is_deprecated(key: str, profile: str = "default") -> bool:
    return key in load_deprecations(profile)


def check_env_for_deprecated(
    env: Dict[str, str], profile: str = "default"
) -> List[dict]:
    """Return list of violations for keys that are deprecated."""
    data = load_deprecations(profile)
    results = []
    for key in env:
        if key in data:
            entry = {"key": key, **data[key]}
            results.append(entry)
    return results


def format_deprecation_results(results: List[dict]) -> str:
    if not results:
        return "No deprecated keys found."
    lines = []
    for r in results:
        line = f"  DEPRECATED  {r['key']}"
        if r.get("reason"):
            line += f" — {r['reason']}"
        if r.get("replacement"):
            line += f" (use '{r['replacement']}' instead)"
        lines.append(line)
    return "\n".join(lines)

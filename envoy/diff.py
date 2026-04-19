"""Diff utilities for comparing .env files."""
from typing import Dict, List, Tuple


def diff_envs(
    base: Dict[str, str], other: Dict[str, str]
) -> Dict[str, List[Tuple[str, str, str]]]:
    """Compare two env dicts and return added, removed, and changed keys."""
    added = []
    removed = []
    changed = []

    for key, value in other.items():
        if key not in base:
            added.append((key, None, value))
        elif base[key] != value:
            changed.append((key, base[key], value))

    for key, value in base.items():
        if key not in other:
            removed.append((key, value, None))

    return {"added": added, "removed": removed, "changed": changed}


def format_diff(diff: Dict[str, List[Tuple[str, str, str]]]) -> str:
    """Format diff result as a human-readable string."""
    lines = []

    for key, _, value in diff["added"]:
        lines.append(f"+ {key}={value}")

    for key, value, _ in diff["removed"]:
        lines.append(f"- {key}={value}")

    for key, old_val, new_val in diff["changed"]:
        lines.append(f"~ {key}: {old_val} -> {new_val}")

    return "\n".join(lines) if lines else "No differences found."


def has_diff(diff: Dict[str, List[Tuple[str, str, str]]]) -> bool:
    """Return True if there are any differences."""
    return any(diff[k] for k in ("added", "removed", "changed"))

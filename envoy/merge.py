"""Merge utilities for combining .env files with conflict resolution."""

from typing import Dict, Optional

MergeStrategy = str
STRATEGY_OURS = "ours"
STRATEGY_THEIRS = "theirs"
STRATEGY_PROMPT = "prompt"


def merge_envs(
    base: Dict[str, str],
    other: Dict[str, str],
    strategy: MergeStrategy = STRATEGY_OURS,
) -> Dict[str, str]:
    """Merge two env dicts. Conflicts resolved by strategy."""
    merged = dict(base)
    conflicts = []

    for key, value in other.items():
        if key not in merged:
            merged[key] = value
        elif merged[key] != value:
            conflicts.append(key)

    for key in conflicts:
        if strategy == STRATEGY_THEIRS:
            merged[key] = other[key]
        elif strategy == STRATEGY_PROMPT:
            print(f"Conflict on '{key}':")
            print(f"  [1] ours:   {merged[key]}")
            print(f"  [2] theirs: {other[key]}")
            choice = input("Choose [1/2]: ").strip()
            if choice == "2":
                merged[key] = other[key]
        # STRATEGY_OURS: keep base value (already set)

    return merged


def merge_summary(
    base: Dict[str, str],
    other: Dict[str, str],
    merged: Dict[str, str],
) -> Dict[str, list]:
    """Return a summary of what was added, overridden, or kept."""
    added = [k for k in other if k not in base]
    conflicts = [k for k in other if k in base and base[k] != other[k]]
    kept = [k for k in conflicts if merged[k] == base[k]]
    overridden = [k for k in conflicts if merged[k] == other[k]]
    return {"added": added, "kept": kept, "overridden": overridden}

"""Reorder keys in an env dict by a given key list, pattern, or priority."""
from typing import Dict, List, Optional


class ReorderError(Exception):
    pass


def reorder_by_list(env: Dict[str, str], order: List[str], append_remaining: bool = True) -> Dict[str, str]:
    """Reorder env keys according to a provided list. Unknown keys appended at end if append_remaining=True."""
    result: Dict[str, str] = {}
    for key in order:
        if key in env:
            result[key] = env[key]
    if append_remaining:
        for key, value in env.items():
            if key not in result:
                result[key] = value
    return result


def reorder_by_prefix_priority(env: Dict[str, str], prefixes: List[str], sep: str = "_") -> Dict[str, str]:
    """Reorder keys so that keys matching prefixes come first, in prefix-priority order."""
    buckets: Dict[str, List[str]] = {p: [] for p in prefixes}
    remaining: List[str] = []
    for key in env:
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix + sep) or key == prefix:
                buckets[prefix].append(key)
                matched = True
                break
        if not matched:
            remaining.append(key)
    result: Dict[str, str] = {}
    for prefix in prefixes:
        for key in sorted(buckets[prefix]):
            result[key] = env[key]
    for key in remaining:
        result[key] = env[key]
    return result


def move_to_top(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Move specified keys to the top, preserving their relative order."""
    missing = [k for k in keys if k not in env]
    if missing:
        raise ReorderError(f"Keys not found in env: {', '.join(missing)}")
    result: Dict[str, str] = {}
    for key in keys:
        result[key] = env[key]
    for key, value in env.items():
        if key not in result:
            result[key] = value
    return result


def move_to_bottom(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Move specified keys to the bottom, preserving their relative order."""
    missing = [k for k in keys if k not in env]
    if missing:
        raise ReorderError(f"Keys not found in env: {', '.join(missing)}")
    result: Dict[str, str] = {}
    for key, value in env.items():
        if key not in keys:
            result[key] = value
    for key in keys:
        result[key] = env[key]
    return result


def format_reorder_diff(original: Dict[str, str], reordered: Dict[str, str]) -> str:
    """Show which keys changed position."""
    orig_keys = list(original.keys())
    new_keys = list(reordered.keys())
    lines = []
    for i, key in enumerate(new_keys):
        orig_pos = orig_keys.index(key) if key in orig_keys else -1
        if orig_pos != i:
            lines.append(f"  {key}: position {orig_pos + 1} -> {i + 1}")
    return "\n".join(lines) if lines else "  (no position changes)"

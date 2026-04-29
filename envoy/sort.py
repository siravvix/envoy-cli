"""Sort and reorder keys in .env files."""

from typing import Dict, List, Optional


def sort_keys(
    env: Dict[str, str],
    reverse: bool = False,
) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items(), key=lambda kv: kv[0], reverse=reverse))


def sort_by_value(
    env: Dict[str, str],
    reverse: bool = False,
) -> Dict[str, str]:
    """Return a new dict with entries sorted by value."""
    return dict(sorted(env.items(), key=lambda kv: kv[1], reverse=reverse))


def group_and_sort(
    env: Dict[str, str],
    separator: str = "_",
) -> Dict[str, str]:
    """Sort keys, grouping by prefix (everything before the first separator)."""

    def prefix_key(kv: tuple) -> tuple:
        k = kv[0]
        parts = k.split(separator, 1)
        prefix = parts[0] if len(parts) > 1 else ""
        return (prefix, k)

    return dict(sorted(env.items(), key=prefix_key))


def move_key(
    env: Dict[str, str],
    key: str,
    position: int,
) -> Dict[str, str]:
    """Move a key to a specific index position. Raises KeyError if key not found."""
    if key not in env:
        raise KeyError(f"Key '{key}' not found in env.")
    items = [(k, v) for k, v in env.items() if k != key]
    position = max(0, min(position, len(items)))
    items.insert(position, (key, env[key]))
    return dict(items)


def custom_order(
    env: Dict[str, str],
    order: List[str],
) -> Dict[str, str]:
    """Reorder env so that keys in `order` appear first (in that order),
    followed by remaining keys in their original relative order."""
    ordered = {k: env[k] for k in order if k in env}
    rest = {k: v for k, v in env.items() if k not in ordered}
    return {**ordered, **rest}


def format_sort_summary(
    original: Dict[str, str],
    sorted_env: Dict[str, str],
) -> str:
    """Return a human-readable summary of how keys were reordered."""
    orig_keys = list(original.keys())
    new_keys = list(sorted_env.keys())
    lines = ["Key order changes:"]
    for new_idx, key in enumerate(new_keys):
        old_idx = orig_keys.index(key)
        if old_idx != new_idx:
            lines.append(f"  {key}: position {old_idx} -> {new_idx}")
    if len(lines) == 1:
        lines.append("  (no changes)")
    return "\n".join(lines)

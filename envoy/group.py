"""Group env keys by prefix or custom label for organized management."""

from typing import Dict, List, Optional


def group_by_prefix(env: Dict[str, str], separator: str = "_") -> Dict[str, Dict[str, str]]:
    """Group env keys by their prefix (first segment before separator)."""
    groups: Dict[str, Dict[str, str]] = {}
    for key, value in env.items():
        if separator in key:
            prefix = key.split(separator)[0]
        else:
            prefix = "__ungrouped__"
        groups.setdefault(prefix, {})[key] = value
    return groups


def group_by_labels(env: Dict[str, str], labels: Dict[str, List[str]]) -> Dict[str, Dict[str, str]]:
    """Group env keys according to a user-defined label mapping.

    labels: {"group_name": ["KEY1", "KEY2", ...]}
    Keys not in any label go into "__unlabeled__".
    """
    groups: Dict[str, Dict[str, str]] = {}
    assigned: set = set()

    for label, keys in labels.items():
        groups[label] = {}
        for key in keys:
            if key in env:
                groups[label][key] = env[key]
                assigned.add(key)

    unlabeled = {k: v for k, v in env.items() if k not in assigned}
    if unlabeled:
        groups["__unlabeled__"] = unlabeled

    return groups


def list_groups(groups: Dict[str, Dict[str, str]]) -> List[str]:
    """Return sorted list of group names."""
    return sorted(groups.keys())


def format_groups(groups: Dict[str, Dict[str, str]], show_values: bool = False) -> str:
    """Format grouped keys for display."""
    lines = []
    for group in sorted(groups.keys()):
        lines.append(f"[{group}]")
        for key, value in sorted(groups[group].items()):
            if show_values:
                lines.append(f"  {key}={value}")
            else:
                lines.append(f"  {key}")
    return "\n".join(lines)


def get_group(groups: Dict[str, Dict[str, str]], name: str) -> Optional[Dict[str, str]]:
    """Retrieve a specific group by name, or None if not found."""
    return groups.get(name)

"""Snapshot comparison utilities for envoy."""
from typing import Dict, List, Tuple
from envoy.diff import diff_envs, format_diff


def compare_snapshots(
    old: Dict[str, str], new: Dict[str, str]
) -> Dict[str, object]:
    """Compare two env snapshots and return a structured result."""
    diff = diff_envs(old, new)
    return {
        "added": diff["added"],
        "removed": diff["removed"],
        "changed": diff["changed"],
        "unchanged": diff["unchanged"],
        "has_changes": bool(diff["added"] or diff["removed"] or diff["changed"]),
    }


def summarize_snapshot(env: Dict[str, str]) -> Dict[str, object]:
    """Return basic stats about a snapshot."""
    return {
        "total_keys": len(env),
        "empty_values": [k for k, v in env.items() if not v],
        "keys": sorted(env.keys()),
    }


def format_snapshot_diff(old: Dict[str, str], new: Dict[str, str]) -> str:
    """Return a human-readable diff string between two snapshots."""
    diff = diff_envs(old, new)
    lines = format_diff(diff)
    if not lines:
        return "No changes between snapshots."
    return "\n".join(lines)


def snapshot_changelog(
    snapshots: List[Tuple[str, Dict[str, str]]]
) -> List[Dict[str, object]]:
    """Given an ordered list of (label, env) tuples, produce a changelog."""
    changelog = []
    for i in range(1, len(snapshots)):
        label_old, env_old = snapshots[i - 1]
        label_new, env_new = snapshots[i]
        result = compare_snapshots(env_old, env_new)
        result["from"] = label_old
        result["to"] = label_new
        changelog.append(result)
    return changelog

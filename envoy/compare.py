"""Compare two .env files or profiles and produce a structured report.

This module builds on top of diff.py and snapshot.py to provide a
higher-level comparison API suitable for CLI output and programmatic use.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envoy.diff import diff_envs, format_diff
from envoy.env_file import parse_env


@dataclass
class CompareReport:
    """Structured result of comparing two env variable sets."""

    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        """Return True if there are any differences."""
        return bool(self.added or self.removed or self.changed)

    @property
    def total_keys(self) -> int:
        """Total number of unique keys across both sides."""
        return len(self.added) + len(self.removed) + len(self.changed) + len(self.unchanged)


def compare_envs(base: Dict[str, str], other: Dict[str, str]) -> CompareReport:
    """Compare two env dicts and return a CompareReport.

    Args:
        base: The reference environment (e.g. current / left side).
        other: The environment to compare against (e.g. incoming / right side).

    Returns:
        A CompareReport with added, removed, changed, and unchanged keys.
    """
    diff = diff_envs(base, other)

    unchanged = {
        k: v
        for k, v in base.items()
        if k not in diff.get("added", {})
        and k not in diff.get("removed", {})
        and k not in diff.get("changed", {})
    }

    return CompareReport(
        added=diff.get("added", {}),
        removed=diff.get("removed", {}),
        changed=diff.get("changed", {}),
        unchanged=unchanged,
    )


def compare_files(path_a: str, path_b: str) -> CompareReport:
    """Load two .env files from disk and compare them.

    Args:
        path_a: Path to the base .env file.
        path_b: Path to the other .env file.

    Returns:
        A CompareReport describing the differences.
    """
    with open(path_a, "r") as f:
        base = parse_env(f.read())
    with open(path_b, "r") as f:
        other = parse_env(f.read())
    return compare_envs(base, other)


def format_report(report: CompareReport, show_unchanged: bool = False) -> str:
    """Render a CompareReport as a human-readable string.

    Args:
        report: The CompareReport to format.
        show_unchanged: If True, also list keys that are the same in both files.

    Returns:
        A formatted multi-line string.
    """
    lines: List[str] = []

    for key, value in sorted(report.added.items()):
        lines.append(f"+ {key}={value}")

    for key, value in sorted(report.removed.items()):
        lines.append(f"- {key}={value}")

    for key, (old_val, new_val) in sorted(report.changed.items()):
        lines.append(f"~ {key}: {old_val!r} -> {new_val!r}")

    if show_unchanged:
        for key, value in sorted(report.unchanged.items()):
            lines.append(f"  {key}={value}")

    if not lines:
        return "No differences found."

    summary_parts = []
    if report.added:
        summary_parts.append(f"{len(report.added)} added")
    if report.removed:
        summary_parts.append(f"{len(report.removed)} removed")
    if report.changed:
        summary_parts.append(f"{len(report.changed)} changed")

    lines.append("")
    lines.append("Summary: " + ", ".join(summary_parts))

    return "\n".join(lines)

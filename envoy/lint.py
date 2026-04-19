"""Lint .env files for common issues."""

from typing import Dict, List, Tuple


LINT_RULES = [
    "no_empty_values",
    "no_duplicate_keys",
    "no_whitespace_in_keys",
    "no_unquoted_special_chars",
]


def lint_env(data: Dict[str, str], rules: List[str] = None) -> List[Tuple[str, str, str]]:
    """Lint env dict. Returns list of (rule, key, message) tuples."""
    if rules is None:
        rules = LINT_RULES
    issues = []

    seen_keys = {}
    if "no_duplicate_keys" in rules:
        # Can't detect from dict alone; handled in lint_lines
        pass

    for key, value in data.items():
        if "no_empty_values" in rules and value == "":
            issues.append(("no_empty_values", key, f"Key '{key}' has an empty value."))

        if "no_whitespace_in_keys" in rules and " " in key:
            issues.append(("no_whitespace_in_keys", key, f"Key '{key}' contains whitespace."))

        if "no_unquoted_special_chars" in rules:
            special = set("#$&|;<>")
            if any(c in value for c in special) and not (
                value.startswith('"') or value.startswith("'")
            ):
                issues.append((
                    "no_unquoted_special_chars", key,
                    f"Key '{key}' value contains special characters and may need quoting."
                ))

    return issues


def lint_lines(lines: List[str], rules: List[str] = None) -> List[Tuple[str, str, str]]:
    """Lint raw lines to catch issues like duplicate keys."""
    if rules is None:
        rules = LINT_RULES
    issues = []
    seen = {}

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if "no_duplicate_keys" in rules:
                if key in seen:
                    issues.append((
                        "no_duplicate_keys", key,
                        f"Key '{key}' is duplicated (first at line {seen[key]}, again at line {lineno})."
                    ))
                else:
                    seen[key] = lineno

    return issues


def format_lint_results(issues: List[Tuple[str, str, str]]) -> str:
    if not issues:
        return "No issues found."
    lines = []
    for rule, key, msg in issues:
        lines.append(f"  [{rule}] {msg}")
    return "\n".join(lines)

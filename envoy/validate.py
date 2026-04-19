"""Validation rules for .env files against a schema."""
from typing import Dict, List, Optional


def validate_env(env: Dict[str, str], schema: Dict[str, dict]) -> List[dict]:
    """
    Validate env dict against a schema.
    Schema format: {KEY: {required: bool, pattern: str, allowed: list}}
    Returns list of violation dicts.
    """
    import re
    violations = []

    for key, rules in schema.items():
        required = rules.get("required", False)
        if key not in env:
            if required:
                violations.append({"key": key, "rule": "required", "message": f"{key} is required but missing"})
            continue

        value = env[key]

        pattern = rules.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            violations.append({"key": key, "rule": "pattern", "message": f"{key} does not match pattern '{pattern}'"})

        allowed = rules.get("allowed")
        if allowed is not None and value not in allowed:
            violations.append({"key": key, "rule": "allowed", "message": f"{key} value '{value}' not in allowed list"})

        min_len = rules.get("min_length")
        if min_len is not None and len(value) < min_len:
            violations.append({"key": key, "rule": "min_length", "message": f"{key} is shorter than min_length {min_len}"})

    return violations


def format_violations(violations: List[dict]) -> str:
    if not violations:
        return "No violations found."
    lines = []
    for v in violations:
        lines.append(f"  [{v['rule']}] {v['message']}")
    return "\n".join(lines)


def load_schema(path: str) -> Dict[str, dict]:
    import json
    with open(path) as f:
        return json.load(f)

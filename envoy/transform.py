"""Key/value transformation utilities for .env files."""

from typing import Dict, Callable, List, Tuple


TransformFn = Callable[[str], str]


def uppercase_keys(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new env dict with all keys uppercased."""
    return {k.upper(): v for k, v in env.items()}


def lowercase_values(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new env dict with all values lowercased."""
    return {k: v.lower() for k, v in env.items()}


def strip_values(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new env dict with all values stripped of surrounding whitespace."""
    return {k: v.strip() for k, v in env.items()}


def add_prefix(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return a new env dict with all keys prefixed."""
    return {f"{prefix}{k}": v for k, v in env.items()}


def remove_prefix(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return a new env dict with prefix stripped from matching keys."""
    result = {}
    for k, v in env.items():
        if k.startswith(prefix):
            result[k[len(prefix):]] = v
        else:
            result[k] = v
    return result


def apply_transform(env: Dict[str, str], fn: TransformFn, target: str = "values") -> Dict[str, str]:
    """Apply an arbitrary transform function to keys or values.

    Args:
        env: Source env dict.
        fn: Callable that accepts a string and returns a string.
        target: 'keys' or 'values'.

    Returns:
        Transformed env dict.
    """
    if target == "keys":
        return {fn(k): v for k, v in env.items()}
    elif target == "values":
        return {k: fn(v) for k, v in env.items()}
    else:
        raise ValueError(f"target must be 'keys' or 'values', got '{target}'")


def format_transform_summary(original: Dict[str, str], transformed: Dict[str, str]) -> List[str]:
    """Produce a human-readable summary of what changed."""
    lines = []
    all_keys = set(original) | set(transformed)
    for key in sorted(all_keys):
        orig_val = original.get(key)
        new_val = transformed.get(key)
        if orig_val is None:
            lines.append(f"  + {key}={new_val}")
        elif new_val is None:
            lines.append(f"  - {key}={orig_val}")
        elif orig_val != new_val:
            lines.append(f"  ~ {key}: {orig_val!r} -> {new_val!r}")
    return lines

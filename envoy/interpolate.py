"""Variable interpolation for .env files.

Supports ${VAR} and $VAR syntax, with optional fallback to os.environ.
"""

import os
import re
from typing import Dict, Optional

_INTERPOLATION_RE = re.compile(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)')


class InterpolationError(Exception):
    """Raised when a referenced variable cannot be resolved."""


def interpolate_value(
    value: str,
    env: Dict[str, str],
    use_os_env: bool = True,
    strict: bool = False,
) -> str:
    """Interpolate variable references in *value* using *env* (and optionally os.environ).

    Args:
        value: The raw string that may contain ``${VAR}`` or ``$VAR`` references.
        env: A mapping of already-known variables (e.g. the current .env dict).
        use_os_env: If True, fall back to ``os.environ`` when a key is absent from *env*.
        strict: If True, raise :class:`InterpolationError` for unresolved references.

    Returns:
        The interpolated string.
    """

    def _resolve(match: re.Match) -> str:
        key = match.group(1) or match.group(2)
        if key in env:
            return env[key]
        if use_os_env and key in os.environ:
            return os.environ[key]
        if strict:
            raise InterpolationError(f"Unresolved variable: {key!r}")
        return match.group(0)  # leave placeholder as-is

    return _INTERPOLATION_RE.sub(_resolve, value)


def interpolate_env(
    env: Dict[str, str],
    use_os_env: bool = True,
    strict: bool = False,
) -> Dict[str, str]:
    """Return a new dict with all values interpolated.

    Variables are resolved in insertion order, so earlier keys can be referenced
    by later ones within the same file.
    """
    resolved: Dict[str, str] = {}
    for key, value in env.items():
        resolved[key] = interpolate_value(value, resolved, use_os_env=use_os_env, strict=strict)
    return resolved


def find_references(value: str) -> list[str]:
    """Return a list of variable names referenced in *value*."""
    return [m.group(1) or m.group(2) for m in _INTERPOLATION_RE.finditer(value)]


def unresolved_references(
    env: Dict[str, str],
    use_os_env: bool = True,
) -> Dict[str, list[str]]:
    """Return a mapping of key -> list of unresolved reference names."""
    result: Dict[str, list[str]] = {}
    for key, value in env.items():
        missing = [
            ref
            for ref in find_references(value)
            if ref not in env and (not use_os_env or ref not in os.environ)
        ]
        if missing:
            result[key] = missing
    return result

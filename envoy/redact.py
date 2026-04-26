"""Redaction utilities for masking sensitive values in .env files.

Provides functions to identify and redact sensitive keys based on
configurable patterns, useful for safe display and logging.
"""

import re
from typing import Dict, List, Optional

# Default patterns that indicate a key holds sensitive data
DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*API_KEY.*",
    r".*APIKEY.*",
    r".*TOKEN.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
    r".*AUTH.*",
    r".*DSN.*",
    r".*DATABASE_URL.*",
]

DEFAULT_MASK = "***"


def is_sensitive(key: str, patterns: Optional[List[str]] = None) -> bool:
    """Return True if the key matches any sensitive pattern.

    Args:
        key: The environment variable key to check.
        patterns: List of regex patterns to match against. Defaults to
                  DEFAULT_SENSITIVE_PATTERNS.

    Returns:
        True if the key is considered sensitive, False otherwise.
    """
    if patterns is None:
        patterns = DEFAULT_SENSITIVE_PATTERNS
    upper_key = key.upper()
    return any(re.fullmatch(pat, upper_key, re.IGNORECASE) for pat in patterns)


def redact_env(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
) -> Dict[str, str]:
    """Return a copy of env with sensitive values replaced by mask.

    Args:
        env: Dictionary of environment variables.
        patterns: Patterns to identify sensitive keys.
        mask: String to replace sensitive values with.

    Returns:
        A new dict with sensitive values masked.
    """
    return {
        key: (mask if is_sensitive(key, patterns) else value)
        for key, value in env.items()
    }


def redact_value(
    key: str,
    value: str,
    patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
) -> str:
    """Return the value masked if the key is sensitive, otherwise unchanged.

    Args:
        key: The environment variable key.
        value: The environment variable value.
        patterns: Patterns to identify sensitive keys.
        mask: String to replace sensitive values with.

    Returns:
        The original value or the mask string.
    """
    return mask if is_sensitive(key, patterns) else value


def list_sensitive_keys(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
) -> List[str]:
    """Return a sorted list of keys in env that are considered sensitive.

    Args:
        env: Dictionary of environment variables.
        patterns: Patterns to identify sensitive keys.

    Returns:
        Sorted list of sensitive key names.
    """
    return sorted(key for key in env if is_sensitive(key, patterns))


def format_redacted(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
) -> str:
    """Format a redacted env dict as KEY=VALUE lines for display.

    Args:
        env: Dictionary of environment variables.
        patterns: Patterns to identify sensitive keys.
        mask: String to replace sensitive values with.

    Returns:
        A multiline string of KEY=VALUE pairs with sensitive values masked.
    """
    redacted = redact_env(env, patterns=patterns, mask=mask)
    return "\n".join(f"{k}={v}" for k, v in redacted.items())

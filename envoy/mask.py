"""Masking utilities for .env values — partially or fully hide sensitive data."""

import re
from typing import Dict, Optional

SENSITIVE_PATTERNS = re.compile(
    r"(password|secret|token|api[_-]?key|private[_-]?key|auth|credential|passwd|pwd)",
    re.IGNORECASE,
)


def is_sensitive_key(key: str) -> bool:
    """Return True if the key name looks sensitive."""
    return bool(SENSITIVE_PATTERNS.search(key))


def mask_value(value: str, mode: str = "partial", char: str = "*") -> str:
    """Mask a string value.

    Modes:
      - 'full'    : replace entire value with asterisks
      - 'partial' : show first 2 and last 2 chars, mask the middle
      - 'length'  : show only the character count, e.g. '<8 chars>'
    """
    if not value:
        return value

    if mode == "full":
        return char * len(value)

    if mode == "length":
        return f"<{len(value)} chars>"

    # partial
    if len(value) <= 4:
        return char * len(value)
    middle_len = len(value) - 4
    return value[:2] + char * middle_len + value[-2:]


def mask_env(
    env: Dict[str, str],
    mode: str = "partial",
    keys: Optional[list] = None,
    auto_detect: bool = True,
    char: str = "*",
) -> Dict[str, str]:
    """Return a copy of env with sensitive values masked.

    Args:
        env: The environment dict.
        mode: Masking mode ('full', 'partial', 'length').
        keys: Explicit list of keys to mask (in addition to auto-detected).
        auto_detect: Whether to auto-detect sensitive keys by name.
        char: Character to use for masking.
    """
    explicit = set(keys or [])
    result = {}
    for k, v in env.items():
        if k in explicit or (auto_detect and is_sensitive_key(k)):
            result[k] = mask_value(v, mode=mode, char=char)
        else:
            result[k] = v
    return result


def list_masked_keys(
    env: Dict[str, str],
    keys: Optional[list] = None,
    auto_detect: bool = True,
) -> list:
    """Return list of keys that would be masked."""
    explicit = set(keys or [])
    return [
        k
        for k in env
        if k in explicit or (auto_detect and is_sensitive_key(k))
    ]

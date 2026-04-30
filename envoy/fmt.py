"""Format .env file contents for consistent style."""

from typing import Dict, List, Tuple


def sort_keys_alpha(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items()))


def align_values(env: Dict[str, str], separator: str = "=") -> List[str]:
    """Return lines with values aligned at the same column."""
    if not env:
        return []
    max_key_len = max(len(k) for k in env)
    lines = []
    for key, value in env.items():
        padding = " " * (max_key_len - len(key))
        lines.append(f"{key}{padding}{separator}{value}")
    return lines


def normalize_quotes(value: str, quote_char: str = '"') -> str:
    """Ensure values containing spaces or special chars are quoted."""
    needs_quoting = any(c in value for c in (" ", "\t", "#", "$", "'", '"'))
    stripped = value.strip('"').strip("'")
    if needs_quoting:
        escaped = stripped.replace(quote_char, f"\\{quote_char}")
        return f"{quote_char}{escaped}{quote_char}"
    return stripped


def remove_blank_lines(lines: List[str]) -> List[str]:
    """Strip consecutive blank lines, keeping single separators."""
    result = []
    prev_blank = False
    for line in lines:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    return result


def format_env(
    env: Dict[str, str],
    sort: bool = False,
    align: bool = False,
    normalize: bool = False,
) -> str:
    """Apply formatting options and return the formatted .env string."""
    if sort:
        env = sort_keys_alpha(env)
    if normalize:
        env = {k: normalize_quotes(v) for k, v in env.items()}
    if align:
        lines = align_values(env)
    else:
        lines = [f"{k}={v}" for k, v in env.items()]
    return "\n".join(lines) + ("\n" if lines else "")

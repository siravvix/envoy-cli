"""Search and filter env variables by key pattern or value."""
import re
from typing import Dict, List, Tuple, Optional


def search_keys(env: Dict[str, str], pattern: str, case_sensitive: bool = False) -> Dict[str, str]:
    """Return entries whose keys match the given regex pattern."""
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = re.compile(pattern, flags)
    return {k: v for k, v in env.items() if compiled.search(k)}


def search_values(env: Dict[str, str], pattern: str, case_sensitive: bool = False) -> Dict[str, str]:
    """Return entries whose values match the given regex pattern."""
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = re.compile(pattern, flags)
    return {k: v for k, v in env.items() if compiled.search(v)}


def search_any(env: Dict[str, str], pattern: str, case_sensitive: bool = False) -> Dict[str, str]:
    """Return entries where key or value matches the pattern."""
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = re.compile(pattern, flags)
    return {k: v for k, v in env.items() if compiled.search(k) or compiled.search(v)}


def filter_by_prefix(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return entries whose keys start with the given prefix."""
    return {k: v for k, v in env.items() if k.startswith(prefix)}


def format_search_results(results: Dict[str, str], pattern: Optional[str] = None) -> str:
    """Format search results for display, optionally highlighting matches."""
    if not results:
        return "No matches found."
    lines = []
    for k, v in results.items():
        lines.append(f"{k}={v}")
    return "\n".join(lines)

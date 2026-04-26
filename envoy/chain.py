"""Chain multiple .env files together with override precedence."""

from typing import Dict, List, Tuple
from envoy.env_file import read_env_file, parse_env


def load_chain(paths: List[str]) -> Dict[str, str]:
    """Load and merge env files in order; later files override earlier ones."""
    merged: Dict[str, str] = {}
    for path in paths:
        content = read_env_file(path)
        env = parse_env(content)
        merged.update(env)
    return merged


def chain_sources(paths: List[str]) -> List[Tuple[str, str, str]]:
    """Return list of (key, value, source_path) showing where each key comes from.

    The last file to define a key wins; the source reflects that file.
    """
    key_source: Dict[str, Tuple[str, str]] = {}
    for path in paths:
        content = read_env_file(path)
        env = parse_env(content)
        for key, value in env.items():
            key_source[key] = (value, path)
    return [(key, val, src) for key, (val, src) in sorted(key_source.items())]


def chain_conflicts(paths: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    """Find keys that are defined in more than one file with different values.

    Returns a dict mapping key -> list of (value, source_path) pairs.
    """
    key_occurrences: Dict[str, List[Tuple[str, str]]] = {}
    for path in paths:
        content = read_env_file(path)
        env = parse_env(content)
        for key, value in env.items():
            key_occurrences.setdefault(key, [])
            key_occurrences[key].append((value, path))

    conflicts = {}
    for key, occurrences in key_occurrences.items():
        values = [v for v, _ in occurrences]
        if len(set(values)) > 1:
            conflicts[key] = occurrences
    return conflicts


def format_chain_sources(sources: List[Tuple[str, str, str]]) -> str:
    """Format chain sources as a human-readable string."""
    if not sources:
        return "(empty)"
    lines = []
    for key, value, src in sources:
        lines.append(f"{key}={value}  ({src})")
    return "\n".join(lines)

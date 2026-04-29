"""Resolve environment variable references across multiple .env files or profiles."""

from typing import Optional
from envoy.env_file import parse_env, read_env_file


class ResolveError(Exception):
    pass


def resolve_key(key: str, sources: list[dict]) -> Optional[str]:
    """Return the first value found for key across sources (last source wins)."""
    result = None
    for source in sources:
        if key in source:
            result = source[key]
    return result


def resolve_all(sources: list[dict]) -> dict:
    """Merge all sources left-to-right, later sources override earlier ones."""
    merged = {}
    for source in sources:
        merged.update(source)
    return merged


def resolve_missing(keys: list[str], sources: list[dict]) -> list[str]:
    """Return keys that are not defined in any source."""
    merged = resolve_all(sources)
    return [k for k in keys if k not in merged]


def resolve_sources_for_key(key: str, sources: list[tuple[str, dict]]) -> list[tuple[str, str]]:
    """Return list of (source_name, value) pairs for all sources defining key."""
    return [(name, env[key]) for name, env in sources if key in env]


def resolve_files(key: str, file_paths: list[str]) -> Optional[str]:
    """Resolve a key across multiple .env files (later files override earlier)."""
    sources = []
    for path in file_paths:
        try:
            content = read_env_file(path)
            sources.append(parse_env(content))
        except FileNotFoundError:
            raise ResolveError(f"File not found: {path}")
    return resolve_key(key, sources)


def format_resolve_trace(key: str, named_sources: list[tuple[str, dict]]) -> str:
    """Format a trace showing which sources define the key and which value wins."""
    hits = resolve_sources_for_key(key, named_sources)
    if not hits:
        return f"{key}: (not found in any source)"
    lines = [f"{key}:"]
    for i, (name, value) in enumerate(hits):
        winner = " <- active" if i == len(hits) - 1 else ""
        lines.append(f"  [{name}] {value}{winner}")
    return "\n".join(lines)

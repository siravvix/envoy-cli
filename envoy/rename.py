"""Rename and copy keys within .env files."""

from typing import Dict, Optional
from envoy.env_file import parse_env, serialize_env


def rename_key(
    env: Dict[str, str],
    old_key: str,
    new_key: str,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Return a new env dict with old_key renamed to new_key."""
    if old_key not in env:
        raise KeyError(f"Key '{old_key}' not found in env.")
    if new_key in env and not overwrite:
        raise ValueError(
            f"Key '{new_key}' already exists. Use overwrite=True to replace it."
        )
    result = dict(env)
    result[new_key] = result.pop(old_key)
    return result


def copy_key(
    env: Dict[str, str],
    src_key: str,
    dest_key: str,
    overwrite: bool = False,
) -> Dict[str, str]:
    """Return a new env dict with src_key copied to dest_key."""
    if src_key not in env:
        raise KeyError(f"Key '{src_key}' not found in env.")
    if dest_key in env and not overwrite:
        raise ValueError(
            f"Key '{dest_key}' already exists. Use overwrite=True to replace it."
        )
    result = dict(env)
    result[dest_key] = result[src_key]
    return result


def rename_key_in_file(
    path: str,
    old_key: str,
    new_key: str,
    overwrite: bool = False,
) -> None:
    """Rename a key directly in a .env file."""
    with open(path, "r") as f:
        content = f.read()
    env = parse_env(content)
    updated = rename_key(env, old_key, new_key, overwrite=overwrite)
    with open(path, "w") as f:
        f.write(serialize_env(updated))


def copy_key_in_file(
    path: str,
    src_key: str,
    dest_key: str,
    overwrite: bool = False,
) -> None:
    """Copy a key directly in a .env file."""
    with open(path, "r") as f:
        content = f.read()
    env = parse_env(content)
    updated = copy_key(env, src_key, dest_key, overwrite=overwrite)
    with open(path, "w") as f:
        f.write(serialize_env(updated))

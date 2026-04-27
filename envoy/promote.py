"""Promote env variables from one profile to another with optional filtering."""

from typing import Optional
from envoy.profiles import load_profile, save_profile


class PromoteError(Exception):
    pass


def promote_keys(
    source: dict,
    target: dict,
    keys: Optional[list] = None,
    overwrite: bool = False,
) -> dict:
    """Promote selected (or all) keys from source into target.

    Returns a new dict representing the merged target.
    """
    result = dict(target)
    to_promote = keys if keys is not None else list(source.keys())

    for key in to_promote:
        if key not in source:
            raise PromoteError(f"Key '{key}' not found in source environment.")
        if key in result and not overwrite:
            raise PromoteError(
                f"Key '{key}' already exists in target. Use overwrite=True to replace."
            )
        result[key] = source[key]

    return result


def promote_summary(source: dict, target: dict, result: dict) -> dict:
    """Return a summary of what changed during promotion."""
    added = [k for k in result if k not in target]
    updated = [k for k in result if k in target and result[k] != target[k]]
    unchanged = [k for k in result if k in target and result[k] == target[k]]
    return {"added": added, "updated": updated, "unchanged": unchanged}


def promote_profile(
    source_profile: str,
    target_profile: str,
    password: str,
    keys: Optional[list] = None,
    overwrite: bool = False,
) -> dict:
    """Load two profiles, promote keys, save target, and return summary."""
    source_env = load_profile(source_profile, password)
    target_env = load_profile(target_profile, password)
    result = promote_keys(source_env, target_env, keys=keys, overwrite=overwrite)
    summary = promote_summary(source_env, target_env, result)
    save_profile(target_profile, result, password)
    return summary

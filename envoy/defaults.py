"""Manage default values for env keys across profiles."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULTS_FILENAME = "defaults.json"


def get_defaults_path(profile: str) -> Path:
    """Return path to the defaults file for a given profile."""
    from envoy.profiles import get_profiles_dir
    return get_profiles_dir() / profile / DEFAULTS_FILENAME


def load_defaults(profile: str) -> Dict[str, str]:
    """Load default values for a profile. Returns empty dict if none exist."""
    path = get_defaults_path(profile)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_defaults(profile: str, defaults: Dict[str, str]) -> None:
    """Persist default values for a profile."""
    path = get_defaults_path(profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(defaults, f, indent=2)


def set_default(profile: str, key: str, value: str) -> None:
    """Set a default value for a key in the given profile."""
    if not key:
        raise ValueError("Key must not be empty.")
    defaults = load_defaults(profile)
    defaults[key] = value
    save_defaults(profile, defaults)


def remove_default(profile: str, key: str) -> bool:
    """Remove a default value. Returns True if it existed, False otherwise."""
    defaults = load_defaults(profile)
    if key not in defaults:
        return False
    del defaults[key]
    save_defaults(profile, defaults)
    return True


def get_default(profile: str, key: str) -> Optional[str]:
    """Return the default value for a key, or None if not set."""
    return load_defaults(profile).get(key)


def apply_defaults(profile: str, env: Dict[str, str]) -> Dict[str, str]:
    """Return a new env dict with defaults applied for any missing keys."""
    defaults = load_defaults(profile)
    result = dict(env)
    for key, value in defaults.items():
        if key not in result:
            result[key] = value
    return result

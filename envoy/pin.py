"""Pin/unpin specific env keys to prevent them from being overwritten during sync or merge."""

import json
from pathlib import Path
from typing import List, Optional

_PINS_FILENAME = ".envoy_pins.json"


def get_pins_path(env_file: str) -> Path:
    """Return the path to the pins file associated with an env file."""
    return Path(env_file).parent / _PINS_FILENAME


def load_pins(env_file: str) -> dict:
    """Load pinned keys for the given env file."""
    path = get_pins_path(env_file)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_pins(env_file: str, pins: dict) -> None:
    """Persist pinned keys to disk."""
    path = get_pins_path(env_file)
    with open(path, "w") as f:
        json.dump(pins, f, indent=2)


def pin_key(env_file: str, key: str, reason: Optional[str] = None) -> None:
    """Pin a key so it is protected from overwrites."""
    pins = load_pins(env_file)
    pins[key] = {"reason": reason or ""}
    save_pins(env_file, pins)


def unpin_key(env_file: str, key: str) -> bool:
    """Unpin a key. Returns True if it was pinned, False otherwise."""
    pins = load_pins(env_file)
    if key not in pins:
        return False
    del pins[key]
    save_pins(env_file, pins)
    return True


def is_pinned(env_file: str, key: str) -> bool:
    """Check whether a key is pinned."""
    return key in load_pins(env_file)


def list_pinned(env_file: str) -> List[str]:
    """Return a sorted list of all pinned keys."""
    return sorted(load_pins(env_file).keys())


def filter_protected(env_file: str, updates: dict) -> dict:
    """Remove pinned keys from an updates dict, returning only safe-to-apply changes."""
    pins = load_pins(env_file)
    return {k: v for k, v in updates.items() if k not in pins}

"""Profile management for envoy-cli: load/save named environment profiles."""

import os
import json
from pathlib import Path

DEFAULT_PROFILES_DIR = Path.home() / ".envoy" / "profiles"


def get_profiles_dir() -> Path:
    profiles_dir = Path(os.environ.get("ENVOY_PROFILES_DIR", DEFAULT_PROFILES_DIR))
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


def list_profiles() -> list[str]:
    """Return a list of available profile names."""
    profiles_dir = get_profiles_dir()
    return [p.stem for p in profiles_dir.glob("*.json")]


def save_profile(name: str, env_path: str, encrypted: bool = False) -> None:
    """Save a named profile pointing to an env file."""
    profiles_dir = get_profiles_dir()
    profile_data = {
        "name": name,
        "env_path": str(Path(env_path).resolve()),
        "encrypted": encrypted,
    }
    profile_file = profiles_dir / f"{name}.json"
    with open(profile_file, "w") as f:
        json.dump(profile_data, f, indent=2)


def load_profile(name: str) -> dict:
    """Load a named profile. Raises FileNotFoundError if not found."""
    profiles_dir = get_profiles_dir()
    profile_file = profiles_dir / f"{name}.json"
    if not profile_file.exists():
        raise FileNotFoundError(f"Profile '{name}' not found.")
    with open(profile_file, "r") as f:
        return json.load(f)


def delete_profile(name: str) -> None:
    """Delete a named profile. Raises FileNotFoundError if not found."""
    profiles_dir = get_profiles_dir()
    profile_file = profiles_dir / f"{name}.json"
    if not profile_file.exists():
        raise FileNotFoundError(f"Profile '{name}' not found.")
    profile_file.unlink()

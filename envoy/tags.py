"""Tag management for .env profiles — assign, list, and filter profiles by tags."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envoy.profiles import get_profiles_dir

TAGS_FILE = "tags.json"


def get_tags_path() -> Path:
    return get_profiles_dir() / TAGS_FILE


def load_tags() -> Dict[str, List[str]]:
    """Return mapping of profile_name -> list of tags."""
    path = get_tags_path()
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def save_tags(tags: Dict[str, List[str]]) -> None:
    path = get_tags_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(tags, f, indent=2)


def add_tag(profile: str, tag: str) -> None:
    """Add a tag to a profile (idempotent)."""
    tags = load_tags()
    profile_tags = tags.get(profile, [])
    if tag not in profile_tags:
        profile_tags.append(tag)
    tags[profile] = profile_tags
    save_tags(tags)


def remove_tag(profile: str, tag: str) -> bool:
    """Remove a tag from a profile. Returns True if tag was present."""
    tags = load_tags()
    profile_tags = tags.get(profile, [])
    if tag not in profile_tags:
        return False
    profile_tags.remove(tag)
    tags[profile] = profile_tags
    save_tags(tags)
    return True


def get_tags(profile: str) -> List[str]:
    """Return tags for a given profile."""
    return load_tags().get(profile, [])


def profiles_with_tag(tag: str) -> List[str]:
    """Return all profiles that have the given tag."""
    tags = load_tags()
    return [profile for profile, ptags in tags.items() if tag in ptags]


def clear_profile_tags(profile: str) -> None:
    """Remove all tags from a profile."""
    tags = load_tags()
    tags.pop(profile, None)
    save_tags(tags)

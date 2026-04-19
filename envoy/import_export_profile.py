"""Import and export profiles to/from portable archive files."""
import json
import zipfile
import os
from pathlib import Path
from envoy.profiles import get_profiles_dir, save_profile, load_profile, list_profiles


def export_profile(profile_name: str, output_path: str) -> None:
    """Export a profile to a .envoy zip archive."""
    data = load_profile(profile_name)
    if data is None:
        raise ValueError(f"Profile '{profile_name}' not found.")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        meta = {"profile": profile_name, "version": 1}
        zf.writestr("meta.json", json.dumps(meta))
        zf.writestr("profile.json", json.dumps(data))


def import_profile(archive_path: str, overwrite: bool = False) -> str:
    """Import a profile from a .envoy zip archive. Returns the profile name."""
    with zipfile.ZipFile(archive_path, 'r') as zf:
        meta = json.loads(zf.read("meta.json"))
        profile_data = json.loads(zf.read("profile.json"))
    profile_name = meta["profile"]
    existing = list_profiles()
    if profile_name in existing and not overwrite:
        raise FileExistsError(
            f"Profile '{profile_name}' already exists. Use overwrite=True to replace."
        )
    save_profile(profile_name, profile_data)
    return profile_name


def export_all_profiles(output_path: str) -> list:
    """Export all profiles into a single zip archive."""
    names = list_profiles()
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        meta = {"profiles": names, "version": 1}
        zf.writestr("meta.json", json.dumps(meta))
        for name in names:
            data = load_profile(name)
            zf.writestr(f"{name}.json", json.dumps(data))
    return names


def import_all_profiles(archive_path: str, overwrite: bool = False) -> list:
    """Import all profiles from a multi-profile zip archive."""
    imported = []
    with zipfile.ZipFile(archive_path, 'r') as zf:
        meta = json.loads(zf.read("meta.json"))
        for name in meta["profiles"]:
            data = json.loads(zf.read(f"{name}.json"))
            existing = list_profiles()
            if name in existing and not overwrite:
                continue
            save_profile(name, data)
            imported.append(name)
    return imported

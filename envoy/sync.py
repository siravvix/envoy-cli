"""Sync module for pushing and pulling .env profiles to/from remote storage.

Currently supports local directory-based remotes and a simple HTTP backend.
Future backends (S3, Vault, etc.) can be added by implementing the RemoteBackend interface.
"""

import os
import json
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from envoy.profiles import get_profiles_dir, save_profile, load_profile


class RemoteBackend(ABC):
    """Abstract base class for remote sync backends."""

    @abstractmethod
    def push(self, profile_name: str, data: bytes) -> None:
        """Upload encrypted profile data to the remote."""
        pass

    @abstractmethod
    def pull(self, profile_name: str) -> bytes:
        """Download encrypted profile data from the remote."""
        pass

    @abstractmethod
    def list_profiles(self) -> list[str]:
        """List available profiles on the remote."""
        pass


class LocalDirectoryBackend(RemoteBackend):
    """Syncs profiles to/from a local directory (useful for shared network drives or testing)."""

    def __init__(self, remote_dir: str):
        self.remote_dir = Path(remote_dir)
        self.remote_dir.mkdir(parents=True, exist_ok=True)

    def push(self, profile_name: str, data: bytes) -> None:
        dest = self.remote_dir / f"{profile_name}.env.enc"
        dest.write_bytes(data)

    def pull(self, profile_name: str) -> bytes:
        src = self.remote_dir / f"{profile_name}.env.enc"
        if not src.exists():
            raise FileNotFoundError(f"Profile '{profile_name}' not found in remote: {self.remote_dir}")
        return src.read_bytes()

    def list_profiles(self) -> list[str]:
        return [
            p.stem.replace(".env", "")
            for p in self.remote_dir.glob("*.env.enc")
        ]


def get_backend(config: dict) -> RemoteBackend:
    """Instantiate a remote backend from a config dict.

    Config keys:
        type (str): Backend type. Currently only 'local' is supported.
        path (str): Required for 'local' backend — path to the remote directory.
    """
    backend_type = config.get("type", "local")
    if backend_type == "local":
        path = config.get("path")
        if not path:
            raise ValueError("Local backend requires a 'path' config value.")
        return LocalDirectoryBackend(path)
    raise ValueError(f"Unsupported backend type: '{backend_type}'")


def compute_checksum(data: bytes) -> str:
    """Return a SHA-256 hex digest of the given bytes."""
    return hashlib.sha256(data).hexdigest()


def push_profile(profile_name: str, backend: RemoteBackend) -> str:
    """Push a locally stored encrypted profile to the remote backend.

    Returns the checksum of the pushed data.
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{profile_name}.env.enc"
    if not profile_path.exists():
        raise FileNotFoundError(f"Local profile '{profile_name}' not found.")
    data = profile_path.read_bytes()
    backend.push(profile_name, data)
    return compute_checksum(data)


def pull_profile(profile_name: str, backend: RemoteBackend) -> str:
    """Pull an encrypted profile from the remote backend and store it locally.

    Returns the checksum of the pulled data.
    """
    data = backend.pull(profile_name)
    profiles_dir = get_profiles_dir()
    profiles_dir.mkdir(parents=True, exist_ok=True)
    dest = profiles_dir / f"{profile_name}.env.enc"
    dest.write_bytes(data)
    return compute_checksum(data)

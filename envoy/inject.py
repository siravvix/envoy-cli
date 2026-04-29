"""Inject env variables into a command's environment and run it."""

from __future__ import annotations

import os
import subprocess
from typing import Dict, List, Optional

from envoy.env_file import read_env_file, parse_env
from envoy.interpolate import interpolate_env


class InjectError(Exception):
    pass


def build_env(
    base: Dict[str, str],
    overrides: Dict[str, str],
    interpolate: bool = False,
) -> Dict[str, str]:
    """Merge base OS env with overrides from the .env file."""
    merged = {**base, **overrides}
    if interpolate:
        merged = interpolate_env(merged, strict=False)
    return merged


def inject_and_run(
    env_path: str,
    command: List[str],
    password: Optional[str] = None,
    interpolate: bool = False,
    inherit_os_env: bool = True,
) -> int:
    """Load *env_path*, inject variables into *command* and execute it.

    Returns the exit code of the subprocess.
    """
    if not command:
        raise InjectError("No command provided.")

    raw = read_env_file(env_path, password=password)
    env_vars = parse_env(raw)

    base = dict(os.environ) if inherit_os_env else {}
    full_env = build_env(base, env_vars, interpolate=interpolate)

    result = subprocess.run(command, env=full_env)  # noqa: S603
    return result.returncode


def preview_env(
    env_path: str,
    password: Optional[str] = None,
    interpolate: bool = False,
    inherit_os_env: bool = False,
) -> Dict[str, str]:
    """Return the environment dict that would be injected, without running anything."""
    raw = read_env_file(env_path, password=password)
    env_vars = parse_env(raw)
    base = dict(os.environ) if inherit_os_env else {}
    return build_env(base, env_vars, interpolate=interpolate)

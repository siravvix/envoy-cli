"""Watch an .env file for changes and trigger actions on modification."""

import time
import os
from pathlib import Path
from typing import Callable, Optional


def get_mtime(path: str) -> float:
    """Return the last modified time of a file."""
    return os.path.getmtime(path)


def watch_file(
    path: str,
    callback: Callable[[str], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Watch a file for changes and call callback(path) when modified.

    Args:
        path: Path to the file to watch.
        callback: Function to call when the file changes.
        interval: Polling interval in seconds.
        max_iterations: Stop after this many iterations (None = forever). Useful for testing.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    last_mtime = get_mtime(path)
    iterations = 0

    while max_iterations is None or iterations < max_iterations:
        time.sleep(interval)
        iterations += 1

        if not file_path.exists():
            break

        current_mtime = get_mtime(path)
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            callback(path)


def make_print_callback(label: str = "changed") -> Callable[[str], None]:
    """Return a simple callback that prints a change notification."""
    def _cb(path: str) -> None:
        print(f"[envoy-watch] {label}: {path}")
    return _cb

"""Track history of env file changes per profile."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

HISTORY_DIR_ENV = "ENVOY_HISTORY_DIR"
DEFAULT_HISTORY_DIR = Path.home() / ".envoy" / "history"


def get_history_dir() -> Path:
    return Path(os.environ.get(HISTORY_DIR_ENV, DEFAULT_HISTORY_DIR))


def get_history_file(profile: str) -> Path:
    return get_history_dir() / f"{profile}.jsonl"


def record_snapshot(profile: str, env: dict, message: str = "") -> None:
    path = get_history_file(profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "env": env,
    }
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_history(profile: str) -> list:
    path = get_history_file(profile)
    if not path.exists():
        return []
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def clear_history(profile: str) -> None:
    path = get_history_file(profile)
    if path.exists():
        path.unlink()


def get_snapshot(profile: str, index: int) -> dict | None:
    entries = read_history(profile)
    if not entries or index >= len(entries):
        return None
    return entries[index]

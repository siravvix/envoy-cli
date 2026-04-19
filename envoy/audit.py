"""Audit log for tracking envoy CLI operations."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

DEFAULT_AUDIT_LOG = Path.home() / ".envoy" / "audit.log"


def get_audit_log_path() -> Path:
    return Path(os.environ.get("ENVOY_AUDIT_LOG", DEFAULT_AUDIT_LOG))


def log_event(action: str, target: str, profile: Optional[str] = None, extra: Optional[dict] = None) -> None:
    """Append a single audit event to the log file."""
    log_path = get_audit_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "target": target,
    }
    if profile:
        entry["profile"] = profile
    if extra:
        entry.update(extra)

    with log_path.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def read_events(limit: Optional[int] = None) -> List[dict]:
    """Read audit events from the log file."""
    log_path = get_audit_log_path()
    if not log_path.exists():
        return []

    with log_path.open("r") as f:
        lines = [line.strip() for line in f if line.strip()]

    events = [json.loads(line) for line in lines]
    if limit:
        events = events[-limit:]
    return events


def clear_events() -> None:
    """Clear the audit log."""
    log_path = get_audit_log_path()
    if log_path.exists():
        log_path.unlink()

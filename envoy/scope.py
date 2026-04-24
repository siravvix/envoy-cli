"""Scope management: assign env vars to named scopes (e.g. dev, staging, prod)."""

import json
from pathlib import Path
from typing import Dict, List, Optional

SCOPES_FILENAME = "scopes.json"
_scopes_dir: Optional[Path] = None


def get_scopes_path() -> Path:
    base = _scopes_dir or (Path.home() / ".envoy")
    base.mkdir(parents=True, exist_ok=True)
    return base / SCOPES_FILENAME


def load_scopes() -> Dict[str, List[str]]:
    path = get_scopes_path()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_scopes(scopes: Dict[str, List[str]]) -> None:
    with open(get_scopes_path(), "w") as f:
        json.dump(scopes, f, indent=2)


def add_key_to_scope(scope: str, key: str) -> None:
    if not scope or not key:
        raise ValueError("scope and key must be non-empty")
    scopes = load_scopes()
    keys = scopes.setdefault(scope, [])
    if key not in keys:
        keys.append(key)
    save_scopes(scopes)


def remove_key_from_scope(scope: str, key: str) -> bool:
    scopes = load_scopes()
    keys = scopes.get(scope, [])
    if key not in keys:
        return False
    keys.remove(key)
    if not keys:
        del scopes[scope]
    save_scopes(scopes)
    return True


def get_scope_keys(scope: str) -> List[str]:
    return load_scopes().get(scope, [])


def list_scopes() -> List[str]:
    return list(load_scopes().keys())


def filter_env_by_scope(env: Dict[str, str], scope: str) -> Dict[str, str]:
    keys = get_scope_keys(scope)
    return {k: v for k, v in env.items() if k in keys}


def delete_scope(scope: str) -> bool:
    scopes = load_scopes()
    if scope not in scopes:
        return False
    del scopes[scope]
    save_scopes(scopes)
    return True

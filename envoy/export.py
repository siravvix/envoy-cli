"""Export .env files to various formats (shell, JSON, YAML, Docker)."""
import json
from typing import Dict

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def export_shell(env: Dict[str, str]) -> str:
    """Export as shell export statements."""
    lines = []
    for key, value in env.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines)


def export_json(env: Dict[str, str], indent: int = 2) -> str:
    """Export as JSON."""
    return json.dumps(env, indent=indent)


def export_yaml(env: Dict[str, str]) -> str:
    """Export as YAML."""
    if not HAS_YAML:
        raise RuntimeError("PyYAML is not installed. Run: pip install pyyaml")
    return yaml.dump(env, default_flow_style=False, sort_keys=True)


def export_docker(env: Dict[str, str]) -> str:
    """Export as Docker --env-file format (key=value, no quotes)."""
    lines = []
    for key, value in env.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines)


FORMATS = {
    "shell": export_shell,
    "json": export_json,
    "yaml": export_yaml,
    "docker": export_docker,
}


def export_env(env: Dict[str, str], fmt: str) -> str:
    """Export env dict to the given format string."""
    if fmt not in FORMATS:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {', '.join(FORMATS)}")
    return FORMATS[fmt](env)

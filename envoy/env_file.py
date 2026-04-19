"""Read, write, encrypt, and decrypt .env files."""

from pathlib import Path
from envoy.crypto import encrypt, decrypt


def parse_env(content: str) -> dict[str, str]:
    """Parse .env file content into a key-value dictionary."""
    env = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def serialize_env(env: dict[str, str]) -> str:
    """Serialize a key-value dictionary to .env file content."""
    return "\n".join(f"{k}={v}" for k, v in env.items()) + "\n"


def read_env_file(path: str) -> dict[str, str]:
    """Read and parse a .env file from disk."""
    content = Path(path).read_text(encoding="utf-8")
    return parse_env(content)


def write_env_file(path: str, env: dict[str, str]) -> None:
    """Write a key-value dictionary to a .env file on disk."""
    Path(path).write_text(serialize_env(env), encoding="utf-8")


def encrypt_env_file(path: str, password: str) -> str:
    """Encrypt a .env file and return the encrypted payload string."""
    content = Path(path).read_text(encoding="utf-8")
    return encrypt(content, password)


def decrypt_env_file(encrypted_payload: str, password: str) -> dict[str, str]:
    """Decrypt an encrypted payload string and return parsed env variables."""
    content = decrypt(encrypted_payload, password)
    return parse_env(content)

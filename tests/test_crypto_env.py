"""Tests for crypto and env_file modules."""

import pytest
from envoy.crypto import encrypt, decrypt
from envoy.env_file import (
    parse_env,
    serialize_env,
    encrypt_env_file,
    decrypt_env_file,
)
from pathlib import Path


PASSWORD = "super-secret-password"

SAMPLE_ENV = """# Database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
SECRET_KEY=abc123
"""


def test_encrypt_decrypt_roundtrip():
    token = encrypt(SAMPLE_ENV, PASSWORD)
    assert isinstance(token, str)
    result = decrypt(token, PASSWORD)
    assert result == SAMPLE_ENV


def test_decrypt_wrong_password():
    from cryptography.exceptions import InvalidTag
    token = encrypt(SAMPLE_ENV, PASSWORD)
    with pytest.raises(InvalidTag):
        decrypt(token, "wrong-password")


def test_parse_env():
    env = parse_env(SAMPLE_ENV)
    assert env["DB_HOST"] == "localhost"
    assert env["DB_PORT"] == "5432"
    assert env["SECRET_KEY"] == "abc123"
    assert len(env) == 4


def test_serialize_env_roundtrip():
    env = parse_env(SAMPLE_ENV)
    serialized = serialize_env(env)
    reparsed = parse_env(serialized)
    assert reparsed == env


def test_encrypt_decrypt_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV, encoding="utf-8")
    payload = encrypt_env_file(str(env_file), PASSWORD)
    result = decrypt_env_file(payload, PASSWORD)
    assert result["DB_NAME"] == "myapp"
    assert result["SECRET_KEY"] == "abc123"

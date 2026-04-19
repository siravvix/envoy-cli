"""Tests for key rotation."""

import os
import pytest
from click.testing import CliRunner
from envoy.env_file import encrypt_env_file, decrypt_env_file
from envoy.rotate import rotate_key, rotate_profile_key
from envoy.cli_rotate import rotate_cli


SAMPLE_ENV = {"DB_HOST": "localhost", "SECRET": "s3cr3t", "PORT": "5432"}


@pytest.fixture
def enc_file(tmp_path):
    path = str(tmp_path / "test.env.enc")
    encrypt_env_file(path, SAMPLE_ENV, "oldpass")
    return path


def test_rotate_key_roundtrip(enc_file):
    result = rotate_key(enc_file, "oldpass", "newpass")
    assert result["status"] == "ok"
    assert result["keys_rotated"] == len(SAMPLE_ENV)
    # old password should no longer work
    with pytest.raises(Exception):
        decrypt_env_file(enc_file, "oldpass")
    # new password should work
    env = decrypt_env_file(enc_file, "newpass")
    assert env == SAMPLE_ENV


def test_rotate_key_wrong_old_password(enc_file):
    with pytest.raises(Exception):
        rotate_key(enc_file, "wrongpass", "newpass")


def test_rotate_profile_key(tmp_path, monkeypatch):
    import envoy.profiles as profiles_mod
    import envoy.rotate as rotate_mod

    monkeypatch.setattr(profiles_mod, "get_profiles_dir", lambda: str(tmp_path))
    monkeypatch.setattr(rotate_mod, "get_profiles_dir".replace("get_", "get_"), profiles_mod.get_profiles_dir, raising=False)

    profile_path = str(tmp_path / "staging.env.enc")
    encrypt_env_file(profile_path, SAMPLE_ENV, "oldpass")

    result = rotate_profile_key("staging", "oldpass", "newpass")
    assert result["profile"] == "staging"
    assert result["keys_rotated"] == len(SAMPLE_ENV)


def test_rotate_profile_not_found(tmp_path, monkeypatch):
    import envoy.profiles as profiles_mod
    monkeypatch.setattr(profiles_mod, "get_profiles_dir", lambda: str(tmp_path))
    with pytest.raises(FileNotFoundError):
        rotate_profile_key("nonexistent", "pass", "newpass")


def test_cli_rotate_file(enc_file):
    runner = CliRunner()
    result = runner.invoke(
        rotate_cli,
        ["file", enc_file, "--old-password", "oldpass", "--new-password", "newpass"],
    )
    assert result.exit_code == 0
    assert "Rotated" in result.output
    assert "3" in result.output


def test_cli_rotate_file_bad_password(enc_file):
    runner = CliRunner()
    result = runner.invoke(
        rotate_cli,
        ["file", enc_file, "--old-password", "wrong", "--new-password", "newpass"],
    )
    assert result.exit_code != 0

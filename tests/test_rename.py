"""Tests for envoy.rename module."""

import pytest
from envoy.rename import rename_key, copy_key, rename_key_in_file, copy_key_in_file


SAMPLE = {"APP_HOST": "localhost", "APP_PORT": "8080", "DEBUG": "true"}


def test_rename_key_basic():
    result = rename_key(SAMPLE, "APP_HOST", "HOST")
    assert "HOST" in result
    assert result["HOST"] == "localhost"
    assert "APP_HOST" not in result


def test_rename_key_missing_raises():
    with pytest.raises(KeyError, match="MISSING"):
        rename_key(SAMPLE, "MISSING", "NEW_KEY")


def test_rename_key_conflict_raises():
    with pytest.raises(ValueError, match="APP_PORT"):
        rename_key(SAMPLE, "APP_HOST", "APP_PORT")


def test_rename_key_conflict_overwrite():
    result = rename_key(SAMPLE, "APP_HOST", "APP_PORT", overwrite=True)
    assert result["APP_PORT"] == "localhost"
    assert "APP_HOST" not in result


def test_rename_key_does_not_mutate_original():
    original = dict(SAMPLE)
    rename_key(original, "APP_HOST", "HOST")
    assert "APP_HOST" in original


def test_copy_key_basic():
    result = copy_key(SAMPLE, "APP_HOST", "HOST_COPY")
    assert result["HOST_COPY"] == "localhost"
    assert result["APP_HOST"] == "localhost"


def test_copy_key_missing_raises():
    with pytest.raises(KeyError, match="MISSING"):
        copy_key(SAMPLE, "MISSING", "DEST")


def test_copy_key_conflict_raises():
    with pytest.raises(ValueError, match="DEBUG"):
        copy_key(SAMPLE, "APP_HOST", "DEBUG")


def test_copy_key_conflict_overwrite():
    result = copy_key(SAMPLE, "APP_HOST", "DEBUG", overwrite=True)
    assert result["DEBUG"] == "localhost"


def test_rename_key_in_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_HOST=localhost\nAPP_PORT=8080\n")
    rename_key_in_file(str(env_file), "APP_HOST", "HOST")
    content = env_file.read_text()
    assert "HOST=localhost" in content
    assert "APP_HOST" not in content


def test_copy_key_in_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_HOST=localhost\nAPP_PORT=8080\n")
    copy_key_in_file(str(env_file), "APP_HOST", "HOST_ALIAS")
    content = env_file.read_text()
    assert "HOST_ALIAS=localhost" in content
    assert "APP_HOST=localhost" in content


def test_rename_key_in_file_missing_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_HOST=localhost\n")
    with pytest.raises(KeyError):
        rename_key_in_file(str(env_file), "NOPE", "NEW")

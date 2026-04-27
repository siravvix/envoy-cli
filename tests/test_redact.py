"""Tests for envoy/redact.py — sensitive key detection and value redaction."""

import pytest
from envoy.redact import (
    is_sensitive,
    redact_env,
    redact_value,
    list_sensitive_keys,
    format_redacted,
)


# ---------------------------------------------------------------------------
# is_sensitive
# ---------------------------------------------------------------------------

def test_is_sensitive_password_key():
    assert is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_secret_key():
    assert is_sensitive("APP_SECRET") is True


def test_is_sensitive_token_key():
    assert is_sensitive("AUTH_TOKEN") is True


def test_is_sensitive_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_private_key():
    assert is_sensitive("PRIVATE_KEY") is True


def test_is_sensitive_case_insensitive():
    assert is_sensitive("db_password") is True
    assert is_sensitive("Api_Key") is True


def test_is_sensitive_non_sensitive_key():
    assert is_sensitive("APP_ENV") is False
    assert is_sensitive("PORT") is False
    assert is_sensitive("DEBUG") is False


def test_is_sensitive_key_containing_sensitive_word():
    # KEY alone should be sensitive (contains 'key')
    assert is_sensitive("ENCRYPTION_KEY") is True


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_redact_value_returns_placeholder():
    result = redact_value("super-secret-value")
    assert result == "***REDACTED***"


def test_redact_value_custom_placeholder():
    result = redact_value("secret", placeholder="<hidden>")
    assert result == "<hidden>"


def test_redact_value_empty_string():
    result = redact_value("")
    assert result == "***REDACTED***"


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

def test_redact_env_replaces_sensitive_keys():
    env = {"DB_PASSWORD": "hunter2", "APP_ENV": "production"}
    result = redact_env(env)
    assert result["DB_PASSWORD"] == "***REDACTED***"
    assert result["APP_ENV"] == "production"


def test_redact_env_does_not_mutate_original():
    env = {"SECRET_KEY": "abc123", "HOST": "localhost"}
    original = dict(env)
    redact_env(env)
    assert env == original


def test_redact_env_all_non_sensitive_unchanged():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = redact_env(env)
    assert result == env


def test_redact_env_custom_placeholder():
    env = {"API_KEY": "real-key", "NAME": "envoy"}
    result = redact_env(env, placeholder="[HIDDEN]")
    assert result["API_KEY"] == "[HIDDEN]"
    assert result["NAME"] == "envoy"


def test_redact_env_empty_dict():
    assert redact_env({}) == {}


# ---------------------------------------------------------------------------
# list_sensitive_keys
# ---------------------------------------------------------------------------

def test_list_sensitive_keys_returns_only_sensitive():
    env = {"DB_PASSWORD": "x", "PORT": "5432", "AUTH_TOKEN": "tok"}
    sensitive = list_sensitive_keys(env)
    assert set(sensitive) == {"DB_PASSWORD", "AUTH_TOKEN"}


def test_list_sensitive_keys_empty_env():
    assert list_sensitive_keys({}) == []


def test_list_sensitive_keys_none_sensitive():
    env = {"HOST": "localhost", "APP_ENV": "dev"}
    assert list_sensitive_keys(env) == []


# ---------------------------------------------------------------------------
# format_redacted
# ---------------------------------------------------------------------------

def test_format_redacted_shows_redacted_marker():
    env = {"DB_PASSWORD": "secret", "APP_ENV": "prod"}
    output = format_redacted(env)
    assert "DB_PASSWORD" in output
    assert "***REDACTED***" in output
    assert "APP_ENV" in output
    assert "prod" in output


def test_format_redacted_empty_env():
    output = format_redacted({})
    assert output == "" or isinstance(output, str)


def test_format_redacted_all_sensitive():
    env = {"API_KEY": "k1", "DB_PASSWORD": "p1"}
    output = format_redacted(env)
    assert "k1" not in output
    assert "p1" not in output
    assert output.count("***REDACTED***") == 2

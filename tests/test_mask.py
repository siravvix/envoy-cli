"""Tests for envoy.mask module."""

import pytest
from envoy.mask import is_sensitive_key, mask_value, mask_env, list_masked_keys


# --- is_sensitive_key ---

def test_is_sensitive_password():
    assert is_sensitive_key("DB_PASSWORD") is True


def test_is_sensitive_secret():
    assert is_sensitive_key("APP_SECRET") is True


def test_is_sensitive_token():
    assert is_sensitive_key("ACCESS_TOKEN") is True


def test_is_sensitive_api_key():
    assert is_sensitive_key("STRIPE_API_KEY") is True


def test_is_not_sensitive_plain():
    assert is_sensitive_key("APP_NAME") is False


def test_is_not_sensitive_port():
    assert is_sensitive_key("PORT") is False


# --- mask_value ---

def test_mask_value_partial_normal():
    result = mask_value("supersecret")
    assert result.startswith("su")
    assert result.endswith("et")
    assert "*" in result


def test_mask_value_partial_short():
    result = mask_value("abc", mode="partial")
    assert result == "***"


def test_mask_value_full():
    result = mask_value("hello", mode="full")
    assert result == "*****"


def test_mask_value_length():
    result = mask_value("hello", mode="length")
    assert result == "<5 chars>"


def test_mask_value_empty_string():
    assert mask_value("") == ""


def test_mask_value_custom_char():
    result = mask_value("password", mode="full", char="#")
    assert result == "########"


# --- mask_env ---

def test_mask_env_auto_detects_sensitive():
    env = {"DB_PASSWORD": "secret123", "APP_NAME": "myapp"}
    result = mask_env(env)
    assert result["APP_NAME"] == "myapp"
    assert "*" in result["DB_PASSWORD"]


def test_mask_env_explicit_key():
    env = {"MY_CUSTOM": "value123", "PORT": "8080"}
    result = mask_env(env, keys=["MY_CUSTOM"])
    assert "*" in result["MY_CUSTOM"]
    assert result["PORT"] == "8080"


def test_mask_env_no_auto_detect():
    env = {"DB_PASSWORD": "secret", "PORT": "5432"}
    result = mask_env(env, auto_detect=False)
    assert result["DB_PASSWORD"] == "secret"


def test_mask_env_does_not_mutate_original():
    env = {"DB_PASSWORD": "secret"}
    mask_env(env)
    assert env["DB_PASSWORD"] == "secret"


# --- list_masked_keys ---

def test_list_masked_keys_detects_sensitive():
    env = {"DB_PASSWORD": "x", "APP_NAME": "y", "SECRET_KEY": "z"}
    keys = list_masked_keys(env)
    assert "DB_PASSWORD" in keys
    assert "SECRET_KEY" in keys
    assert "APP_NAME" not in keys


def test_list_masked_keys_explicit():
    env = {"CUSTOM": "val", "OTHER": "val2"}
    keys = list_masked_keys(env, keys=["CUSTOM"], auto_detect=False)
    assert keys == ["CUSTOM"]


def test_list_masked_keys_empty_env():
    assert list_masked_keys({}) == []

"""Tests for envoy.search module."""
import pytest
from envoy.search import search_keys, search_values, search_any, filter_by_prefix, format_search_results

SAMPLE = {
    "DATABASE_URL": "postgres://localhost/db",
    "REDIS_URL": "redis://localhost:6379",
    "SECRET_KEY": "supersecret",
    "DEBUG": "true",
    "APP_NAME": "envoy",
}


def test_search_keys_basic():
    result = search_keys(SAMPLE, "URL")
    assert "DATABASE_URL" in result
    assert "REDIS_URL" in result
    assert "SECRET_KEY" not in result


def test_search_keys_case_insensitive():
    result = search_keys(SAMPLE, "url")
    assert "DATABASE_URL" in result


def test_search_keys_case_sensitive_no_match():
    result = search_keys(SAMPLE, "url", case_sensitive=True)
    assert result == {}


def test_search_values_basic():
    result = search_values(SAMPLE, "localhost")
    assert "DATABASE_URL" in result
    assert "REDIS_URL" in result
    assert "SECRET_KEY" not in result


def test_search_values_no_match():
    result = search_values(SAMPLE, "nonexistent")
    assert result == {}


def test_search_any_matches_key_or_value():
    result = search_any(SAMPLE, "secret")
    assert "SECRET_KEY" in result  # matches key
    assert "SECRET_KEY" in result  # value also contains 'secret'


def test_filter_by_prefix():
    result = filter_by_prefix(SAMPLE, "APP_")
    assert result == {"APP_NAME": "envoy"}


def test_filter_by_prefix_no_match():
    result = filter_by_prefix(SAMPLE, "MISSING_")
    assert result == {}


def test_format_search_results_empty():
    assert format_search_results({}) == "No matches found."


def test_format_search_results_output():
    result = format_search_results({"KEY": "value"})
    assert "KEY=value" in result

"""Tests for envoy.cast module."""

import pytest
from envoy.cast import cast_value, cast_env, format_cast_result, CastError, SUPPORTED_TYPES


# --- cast_value ---

def test_cast_str_passthrough():
    assert cast_value("hello", "str") == "hello"


def test_cast_int_valid():
    assert cast_value("42", "int") == 42


def test_cast_int_invalid():
    with pytest.raises(CastError, match="Cannot cast"):
        cast_value("abc", "int")


def test_cast_float_valid():
    assert cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_float_invalid():
    with pytest.raises(CastError):
        cast_value("not_a_float", "float")


@pytest.mark.parametrize("raw,expected", [
    ("true", True),
    ("True", True),
    ("1", True),
    ("yes", True),
    ("on", True),
    ("false", False),
    ("False", False),
    ("0", False),
    ("no", False),
    ("off", False),
])
def test_cast_bool_valid(raw, expected):
    assert cast_value(raw, "bool") is expected


def test_cast_bool_invalid():
    with pytest.raises(CastError, match="Cannot cast"):
        cast_value("maybe", "bool")


def test_cast_list_basic():
    assert cast_value("a,b,c", "list") == ["a", "b", "c"]


def test_cast_list_trims_spaces():
    assert cast_value(" a , b , c ", "list") == ["a", "b", "c"]


def test_cast_list_single_item():
    assert cast_value("only", "list") == ["only"]


def test_cast_unsupported_type():
    with pytest.raises(CastError, match="Unsupported type"):
        cast_value("x", "dict")


# --- cast_env ---

def test_cast_env_basic():
    env = {"PORT": "8080", "DEBUG": "true", "NAME": "app"}
    schema = {"PORT": "int", "DEBUG": "bool"}
    result = cast_env(env, schema)
    assert result["PORT"] == 8080
    assert result["DEBUG"] is True
    assert result["NAME"] == "app"


def test_cast_env_missing_key_in_schema_is_skipped():
    env = {"A": "1"}
    schema = {"B": "int"}
    result = cast_env(env, schema)
    assert result["A"] == "1"


def test_cast_env_raises_on_invalid():
    env = {"PORT": "not_a_number"}
    schema = {"PORT": "int"}
    with pytest.raises(CastError, match="Cast errors"):
        cast_env(env, schema)


# --- format_cast_result ---

def test_format_cast_result_contains_type():
    result = {"PORT": 8080, "DEBUG": True, "NAME": "app"}
    output = format_cast_result(result)
    assert "int" in output
    assert "bool" in output
    assert "str" in output
    assert "PORT" in output


# --- SUPPORTED_TYPES ---

def test_supported_types_list():
    assert "int" in SUPPORTED_TYPES
    assert "bool" in SUPPORTED_TYPES
    assert "list" in SUPPORTED_TYPES

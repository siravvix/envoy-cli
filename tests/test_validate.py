"""Tests for envoy.validate module and CLI."""
import json
import pytest
from click.testing import CliRunner
from envoy.validate import validate_env, format_violations
from envoy.cli_validate import validate_cli


SCHEMA = {
    "APP_ENV": {"required": True, "allowed": ["development", "staging", "production"]},
    "PORT": {"required": True, "pattern": r"\d+"},
    "SECRET_KEY": {"required": True, "min_length": 8},
    "OPTIONAL_KEY": {"required": False},
}


def test_validate_passes():
    env = {"APP_ENV": "production", "PORT": "8080", "SECRET_KEY": "supersecret"}
    violations = validate_env(env, SCHEMA)
    assert violations == []


def test_validate_missing_required():
    env = {"PORT": "8080", "SECRET_KEY": "supersecret"}
    violations = validate_env(env, SCHEMA)
    assert any(v["key"] == "APP_ENV" and v["rule"] == "required" for v in violations)


def test_validate_pattern_fail():
    env = {"APP_ENV": "production", "PORT": "abc", "SECRET_KEY": "supersecret"}
    violations = validate_env(env, SCHEMA)
    assert any(v["key"] == "PORT" and v["rule"] == "pattern" for v in violations)


def test_validate_allowed_fail():
    env = {"APP_ENV": "local", "PORT": "8080", "SECRET_KEY": "supersecret"}
    violations = validate_env(env, SCHEMA)
    assert any(v["key"] == "APP_ENV" and v["rule"] == "allowed" for v in violations)


def test_validate_min_length_fail():
    env = {"APP_ENV": "production", "PORT": "8080", "SECRET_KEY": "short"}
    violations = validate_env(env, SCHEMA)
    assert any(v["key"] == "SECRET_KEY" and v["rule"] == "min_length" for v in violations)


def test_format_violations_empty():
    assert "No violations" in format_violations([])


def test_format_violations_nonempty():
    violations = [{"key": "PORT", "rule": "pattern", "message": "PORT does not match pattern"}]
    result = format_violations(violations)
    assert "pattern" in result and "PORT" in result


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_check_passes(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_ENV=production\nPORT=8080\nSECRET_KEY=supersecret\n")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(SCHEMA))
    result = runner.invoke(validate_cli, ["check", str(env_file), str(schema_file)])
    assert result.exit_code == 0
    assert "All checks passed" in result.output


def test_cli_check_violations(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\nSECRET_KEY=supersecret\n")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(SCHEMA))
    result = runner.invoke(validate_cli, ["check", str(env_file), str(schema_file)])
    assert "violation" in result.output


def test_cli_check_strict_exits(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\n")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(SCHEMA))
    result = runner.invoke(validate_cli, ["check", str(env_file), str(schema_file), "--strict"])
    assert result.exit_code != 0

"""Tests for envoy/export.py"""
import json
import pytest
from envoy.export import export_shell, export_json, export_docker, export_env


SAMPLE = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "SECRET": 'has"quote',
}


def test_export_shell_basic():
    result = export_shell({"FOO": "bar"})
    assert result == 'export FOO="bar"'


def test_export_shell_escapes_quotes():
    result = export_shell({"KEY": 'val"ue'})
    assert '\\"' in result


def test_export_shell_multiple_keys():
    result = export_shell({"A": "1", "B": "2"})
    lines = result.splitlines()
    assert len(lines) == 2
    assert all(line.startswith("export ") for line in lines)


def test_export_json_valid():
    result = export_json({"FOO": "bar"})
    parsed = json.loads(result)
    assert parsed == {"FOO": "bar"}


def test_export_json_indent():
    result = export_json({"A": "1"}, indent=4)
    assert "    " in result


def test_export_docker_no_quotes():
    result = export_docker({"FOO": "bar"})
    assert result == "FOO=bar"
    assert '"' not in result


def test_export_docker_multiple():
    result = export_docker({"A": "1", "B": "2"})
    lines = result.splitlines()
    assert "A=1" in lines
    assert "B=2" in lines


def test_export_env_dispatch():
    result = export_env({"X": "y"}, "json")
    assert json.loads(result) == {"X": "y"}


def test_export_env_unknown_format():
    with pytest.raises(ValueError, match="Unknown format"):
        export_env({}, "xml")


def test_export_shell_empty():
    assert export_shell({}) == ""


def test_export_docker_empty():
    assert export_docker({}) == ""

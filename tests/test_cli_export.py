"""Tests for envoy/cli_export.py"""
import os
import json
import pytest
from click.testing import CliRunner
from envoy.cli_export import export_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nDEBUG=true\n")
    return str(p)


def test_convert_shell(runner, env_file):
    result = runner.invoke(export_cli, ["convert", env_file, "--format", "shell"])
    assert result.exit_code == 0
    assert 'export FOO="bar"' in result.output
    assert 'export DEBUG="true"' in result.output


def test_convert_json(runner, env_file):
    result = runner.invoke(export_cli, ["convert", env_file, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["FOO"] == "bar"


def test_convert_docker(runner, env_file):
    result = runner.invoke(export_cli, ["convert", env_file, "--format", "docker"])
    assert result.exit_code == 0
    assert "FOO=bar" in result.output


def test_convert_to_output_file(runner, env_file, tmp_path):
    out = str(tmp_path / "out.json")
    result = runner.invoke(export_cli, ["convert", env_file, "--format", "json", "--output", out])
    assert result.exit_code == 0
    assert os.path.exists(out)
    with open(out) as f:
        data = json.load(f)
    assert data["FOO"] == "bar"


def test_list_formats(runner):
    result = runner.invoke(export_cli, ["formats"])
    assert result.exit_code == 0
    for fmt in ("shell", "json", "docker"):
        assert fmt in result.output


def test_convert_missing_file(runner):
    result = runner.invoke(export_cli, ["convert", "nonexistent.env"])
    assert result.exit_code != 0

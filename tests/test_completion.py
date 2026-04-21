"""Tests for envoy/completion.py and envoy/cli_completion.py."""

import os
import pytest
from click.testing import CliRunner

from envoy.completion import (
    get_env_keys,
    get_profile_names,
    generate_bash_completion,
    generate_zsh_completion,
)
from envoy.cli_completion import completion_cli


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\nSECRET=hunter2\n")
    return str(f)


@pytest.fixture
def set_profiles_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_PROFILES_DIR", str(tmp_path / "profiles"))
    os.makedirs(str(tmp_path / "profiles"), exist_ok=True)
    return tmp_path / "profiles"


def test_get_env_keys_returns_all_keys(env_file):
    keys = get_env_keys(env_file)
    assert set(keys) == {"FOO", "BAZ", "SECRET"}


def test_get_env_keys_missing_file():
    keys = get_env_keys("/nonexistent/path/.env")
    assert keys == []


def test_get_profile_names_empty(set_profiles_dir):
    names = get_profile_names()
    assert names == []


def test_get_profile_names_with_profiles(set_profiles_dir):
    from envoy.profiles import save_profile
    save_profile("dev", {"KEY": "val"}, "pass")
    save_profile("prod", {"KEY": "val"}, "pass")
    names = get_profile_names()
    assert "dev" in names
    assert "prod" in names


def test_generate_bash_completion_contains_script_name():
    script = generate_bash_completion("envoy")
    assert "envoy" in script
    assert "COMPREPLY" in script
    assert "complete -F" in script


def test_generate_zsh_completion_contains_commands():
    script = generate_zsh_completion("envoy")
    assert "#compdef envoy" in script
    assert "encrypt" in script
    assert "decrypt" in script


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_install_bash(runner):
    result = runner.invoke(completion_cli, ["install", "bash"])
    assert result.exit_code == 0
    assert "COMPREPLY" in result.output


def test_cli_install_zsh(runner):
    result = runner.invoke(completion_cli, ["install", "zsh"])
    assert result.exit_code == 0
    assert "#compdef" in result.output


def test_cli_keys_command(runner, env_file):
    result = runner.invoke(completion_cli, ["keys", env_file])
    assert result.exit_code == 0
    assert "FOO" in result.output
    assert "BAZ" in result.output


def test_cli_profiles_command(runner, set_profiles_dir):
    from envoy.profiles import save_profile
    save_profile("staging", {"X": "1"}, "pw")
    result = runner.invoke(completion_cli, ["profiles"])
    assert result.exit_code == 0
    assert "staging" in result.output

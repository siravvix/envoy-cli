"""Tests for envoy.tags and envoy.cli_tags."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.tags import (
    add_tag,
    remove_tag,
    get_tags,
    profiles_with_tag,
    clear_profile_tags,
    load_tags,
)
from envoy.cli_tags import tags_cli
from envoy import profiles as profiles_mod
from envoy import tags as tags_mod


@pytest.fixture(autouse=True)
def set_profiles_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(profiles_mod, "get_profiles_dir", lambda: tmp_path)
    monkeypatch.setattr(tags_mod, "get_profiles_dir", lambda: tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_add_tag_new():
    add_tag("production", "live")
    assert "live" in get_tags("production")


def test_add_tag_idempotent():
    add_tag("production", "live")
    add_tag("production", "live")
    assert get_tags("production").count("live") == 1


def test_remove_tag_existing():
    add_tag("staging", "test")
    result = remove_tag("staging", "test")
    assert result is True
    assert "test" not in get_tags("staging")


def test_remove_tag_missing():
    result = remove_tag("staging", "nonexistent")
    assert result is False


def test_profiles_with_tag():
    add_tag("prod", "live")
    add_tag("staging", "live")
    add_tag("dev", "local")
    found = profiles_with_tag("live")
    assert "prod" in found
    assert "staging" in found
    assert "dev" not in found


def test_clear_profile_tags():
    add_tag("dev", "local")
    add_tag("dev", "debug")
    clear_profile_tags("dev")
    assert get_tags("dev") == []


def test_cli_add(runner):
    result = runner.invoke(tags_cli, ["add", "myprofile", "mytag"])
    assert result.exit_code == 0
    assert "added" in result.output
    assert "mytag" in get_tags("myprofile")


def test_cli_remove(runner):
    add_tag("myprofile", "mytag")
    result = runner.invoke(tags_cli, ["remove", "myprofile", "mytag"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_remove_missing(runner):
    result = runner.invoke(tags_cli, ["remove", "myprofile", "ghost"])
    assert result.exit_code != 0


def test_cli_list(runner):
    add_tag("env1", "alpha")
    add_tag("env1", "beta")
    result = runner.invoke(tags_cli, ["list", "env1"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_cli_find(runner):
    add_tag("prod", "shared")
    add_tag("staging", "shared")
    result = runner.invoke(tags_cli, ["find", "shared"])
    assert "prod" in result.output
    assert "staging" in result.output


def test_cli_clear(runner):
    add_tag("env2", "x")
    result = runner.invoke(tags_cli, ["clear", "env2"])
    assert result.exit_code == 0
    assert get_tags("env2") == []

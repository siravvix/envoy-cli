"""Tests for envoy.alias and envoy.cli_alias."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy.alias import (
    add_alias,
    format_aliases,
    list_aliases,
    remove_alias,
    resolve_alias,
)
from envoy.cli_alias import alias_cli


@pytest.fixture()
def aliases_dir(tmp_path, monkeypatch):
    import envoy.alias as _mod

    monkeypatch.setattr(_mod, "get_aliases_path", lambda base_dir=None: tmp_path / "aliases.json")
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def test_add_and_resolve(aliases_dir):
    add_alias("db", "DATABASE_URL", base_dir=aliases_dir)
    assert resolve_alias("db", base_dir=aliases_dir) == "DATABASE_URL"


def test_resolve_missing_returns_none(aliases_dir):
    assert resolve_alias("nope", base_dir=aliases_dir) is None


def test_add_alias_empty_raises(aliases_dir):
    with pytest.raises(ValueError):
        add_alias("", "KEY", base_dir=aliases_dir)
    with pytest.raises(ValueError):
        add_alias("alias", "", base_dir=aliases_dir)


def test_remove_alias(aliases_dir):
    add_alias("x", "X_KEY", base_dir=aliases_dir)
    remove_alias("x", base_dir=aliases_dir)
    assert resolve_alias("x", base_dir=aliases_dir) is None


def test_remove_missing_raises(aliases_dir):
    with pytest.raises(KeyError):
        remove_alias("ghost", base_dir=aliases_dir)


def test_list_aliases(aliases_dir):
    add_alias("a", "A_KEY", base_dir=aliases_dir)
    add_alias("b", "B_KEY", base_dir=aliases_dir)
    result = list_aliases(base_dir=aliases_dir)
    assert result == {"a": "A_KEY", "b": "B_KEY"}


def test_format_aliases_empty():
    assert format_aliases({}) == "(no aliases defined)"


def test_format_aliases_output():
    out = format_aliases({"db": "DATABASE_URL", "s": "SECRET_KEY"})
    assert "->" in out
    assert "DATABASE_URL" in out


def test_cli_add_and_list(runner, aliases_dir):
    result = runner.invoke(alias_cli, ["add", "db", "DATABASE_URL"])
    assert result.exit_code == 0
    assert "saved" in result.output

    result = runner.invoke(alias_cli, ["list"])
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output


def test_cli_remove(runner, aliases_dir):
    runner.invoke(alias_cli, ["add", "tmp", "TMP_KEY"])
    result = runner.invoke(alias_cli, ["remove", "tmp"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_resolve(runner, aliases_dir):
    runner.invoke(alias_cli, ["add", "port", "PORT"])
    result = runner.invoke(alias_cli, ["resolve", "port"])
    assert result.exit_code == 0
    assert "PORT" in result.output


def test_cli_resolve_missing(runner, aliases_dir):
    result = runner.invoke(alias_cli, ["resolve", "missing"])
    assert result.exit_code != 0

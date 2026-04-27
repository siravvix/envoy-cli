"""Tests for envoy.freeze and envoy.cli_freeze."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envoy.freeze import (
    freeze_file,
    unfreeze_file,
    is_frozen,
    list_frozen,
    assert_not_frozen,
    get_freeze_index_path,
)
from envoy.cli_freeze import freeze_cli


@pytest.fixture(autouse=True)
def freeze_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.freeze.get_freeze_index_path",
                        lambda directory=None: get_freeze_index_path(str(tmp_path)))
    return tmp_path


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return str(f)


@pytest.fixture
def runner():
    return CliRunner()


def test_freeze_and_is_frozen(env_file, tmp_path):
    freeze_file(env_file, str(tmp_path))
    assert is_frozen(env_file, str(tmp_path)) is True


def test_unfreeze_removes_freeze(env_file, tmp_path):
    freeze_file(env_file, str(tmp_path))
    result = unfreeze_file(env_file, str(tmp_path))
    assert result is True
    assert is_frozen(env_file, str(tmp_path)) is False


def test_unfreeze_not_frozen_returns_false(env_file, tmp_path):
    result = unfreeze_file(env_file, str(tmp_path))
    assert result is False


def test_list_frozen_empty(tmp_path):
    assert list_frozen(str(tmp_path)) == []


def test_list_frozen_multiple(tmp_path):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_text("A=1")
    f2.write_text("B=2")
    freeze_file(str(f1), str(tmp_path))
    freeze_file(str(f2), str(tmp_path))
    frozen = list_frozen(str(tmp_path))
    assert len(frozen) == 2


def test_assert_not_frozen_raises(env_file, tmp_path):
    freeze_file(env_file, str(tmp_path))
    with pytest.raises(PermissionError, match="frozen"):
        assert_not_frozen(env_file, str(tmp_path))


def test_assert_not_frozen_passes_when_not_frozen(env_file, tmp_path):
    assert_not_frozen(env_file, str(tmp_path))  # should not raise


def test_freeze_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        freeze_file(str(tmp_path / "missing.env"), str(tmp_path))


def test_cli_lock_and_status(runner, env_file, tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.cli_freeze.freeze_file",
                        lambda fp, directory=None: freeze_file(fp, str(tmp_path)))
    monkeypatch.setattr("envoy.cli_freeze.is_frozen",
                        lambda fp, directory=None: is_frozen(fp, str(tmp_path)))
    result = runner.invoke(freeze_cli, ["lock", env_file])
    assert result.exit_code == 0
    assert "Frozen" in result.output


def test_cli_list_empty(runner, tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.cli_freeze.list_frozen",
                        lambda directory=None: list_frozen(str(tmp_path)))
    result = runner.invoke(freeze_cli, ["list"])
    assert result.exit_code == 0
    assert "No files" in result.output

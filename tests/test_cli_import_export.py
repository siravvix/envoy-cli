"""Tests for transfer CLI commands."""
import os
import pytest
from click.testing import CliRunner
from envoy.cli_import_export import transfer_cli
from envoy.profiles import save_profile, delete_profile, list_profiles


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def set_profiles_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.profiles.PROFILES_DIR", str(tmp_path / "profiles"))
    monkeypatch.setattr("envoy.import_export_profile.get_profiles_dir",
                        lambda: str(tmp_path / "profiles"))
    os.makedirs(str(tmp_path / "profiles"), exist_ok=True)
    return tmp_path


def test_export_command(runner, tmp_path):
    save_profile("staging", {"ciphertext": "c", "salt": "s"})
    out = str(tmp_path / "staging.envoy")
    result = runner.invoke(transfer_cli, ["export", "staging", out])
    assert result.exit_code == 0
    assert "Exported profile 'staging'" in result.output
    assert os.path.exists(out)


def test_export_missing_profile(runner, tmp_path):
    out = str(tmp_path / "missing.envoy")
    result = runner.invoke(transfer_cli, ["export", "ghost", out])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_import_command(runner, tmp_path):
    save_profile("qa", {"ciphertext": "q", "salt": "s"})
    out = str(tmp_path / "qa.envoy")
    runner.invoke(transfer_cli, ["export", "qa", out])
    delete_profile("qa")
    result = runner.invoke(transfer_cli, ["import", out])
    assert result.exit_code == 0
    assert "Imported profile 'qa'" in result.output


def test_import_existing_without_overwrite(runner, tmp_path):
    save_profile("qa", {"ciphertext": "q", "salt": "s"})
    out = str(tmp_path / "qa.envoy")
    runner.invoke(transfer_cli, ["export", "qa", out])
    result = runner.invoke(transfer_cli, ["import", out])
    assert result.exit_code == 1


def test_export_all_and_import_all(runner, tmp_path):
    save_profile("p1", {"ciphertext": "1", "salt": "s"})
    save_profile("p2", {"ciphertext": "2", "salt": "s"})
    out = str(tmp_path / "all.envoy")
    result = runner.invoke(transfer_cli, ["export-all", out])
    assert result.exit_code == 0
    assert "2 profile(s)" in result.output
    delete_profile("p1")
    delete_profile("p2")
    result = runner.invoke(transfer_cli, ["import-all", out])
    assert result.exit_code == 0
    assert "2 profile(s)" in result.output

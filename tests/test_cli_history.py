import pytest
from click.testing import CliRunner
from envoy.cli_history import history_cli
from envoy.history import record_snapshot, HISTORY_DIR_ENV


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def set_history_dir(tmp_path, monkeypatch):
    monkeypatch.setenv(HISTORY_DIR_ENV, str(tmp_path / "history"))


def test_list_empty(runner):
    result = runner.invoke(history_cli, ["list", "dev"])
    assert result.exit_code == 0
    assert "No history" in result.output


def test_list_with_entries(runner):
    record_snapshot("dev", {"KEY": "val"}, message="first commit")
    result = runner.invoke(history_cli, ["list", "dev"])
    assert result.exit_code == 0
    assert "first commit" in result.output
    assert "[0]" in result.output


def test_show_snapshot(runner):
    record_snapshot("dev", {"FOO": "bar"})
    result = runner.invoke(history_cli, ["show", "dev", "0"])
    assert result.exit_code == 0
    assert "FOO=bar" in result.output


def test_show_missing_snapshot(runner):
    result = runner.invoke(history_cli, ["show", "dev", "99"])
    assert result.exit_code != 0


def test_restore_snapshot(runner, tmp_path):
    record_snapshot("dev", {"RESTORE": "yes"})
    out = str(tmp_path / "out.env")
    result = runner.invoke(history_cli, ["restore", "dev", "0", out])
    assert result.exit_code == 0
    assert "Restored" in result.output
    content = open(out).read()
    assert "RESTORE=yes" in content


def test_clear_history(runner):
    record_snapshot("dev", {"X": "1"})
    result = runner.invoke(history_cli, ["clear", "dev"])
    assert result.exit_code == 0
    assert "cleared" in result.output

import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=mysecret\n")
    return env_file


def test_show_command(runner, sample_env):
    result = runner.invoke(cli, ["show", str(sample_env)])
    assert result.exit_code == 0
    assert "DB_HOST=***" in result.output
    assert "DB_PORT=***" in result.output
    assert "mysecret" not in result.output


def test_get_command(runner, sample_env):
    result = runner.invoke(cli, ["get", str(sample_env), "DB_HOST"])
    assert result.exit_code == 0
    assert "localhost" in result.output


def test_get_missing_key(runner, sample_env):
    result = runner.invoke(cli, ["get", str(sample_env), "MISSING_KEY"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_encrypt_decrypt_roundtrip_cli(runner, sample_env, tmp_path):
    enc_file = tmp_path / ".env.enc"
    dec_file = tmp_path / ".env.dec"
    password = "testpassword"

    result = runner.invoke(cli, ["encrypt", str(sample_env), "--password", password, "--output", str(enc_file)])
    assert result.exit_code == 0
    assert enc_file.exists()

    result = runner.invoke(cli, ["decrypt", str(enc_file), "--password", password, "--output", str(dec_file)])
    assert result.exit_code == 0
    assert dec_file.exists()
    content = dec_file.read_text()
    assert "DB_HOST=localhost" in content


def test_decrypt_wrong_password_cli(runner, sample_env, tmp_path):
    enc_file = tmp_path / ".env.enc"
    dec_file = tmp_path / ".env.dec"

    runner.invoke(cli, ["encrypt", str(sample_env), "--password", "correct", "--output", str(enc_file)])
    result = runner.invoke(cli, ["decrypt", str(enc_file), "--password", "wrong", "--output", str(dec_file)])
    assert result.exit_code != 0
    assert "Decryption failed" in result.output


def test_encrypt_missing_file(runner, tmp_path):
    result = runner.invoke(cli, ["encrypt", str(tmp_path / "nonexistent.env"), "--password", "pw"])
    assert result.exit_code != 0
    assert "not found" in result.output

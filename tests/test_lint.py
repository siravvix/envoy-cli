"""Tests for envoy.lint and envoy.cli_lint."""

import pytest
from click.testing import CliRunner
from envoy.lint import lint_env, lint_lines, format_lint_results
from envoy.cli_lint import lint_cli


def test_lint_empty_value():
    issues = lint_env({"FOO": "", "BAR": "ok"})
    rules = [r for r, _, _ in issues]
    assert "no_empty_values" in rules
    keys = [k for _, k, _ in issues]
    assert "FOO" in keys


def test_lint_whitespace_in_key():
    issues = lint_env({"MY KEY": "value"})
    rules = [r for r, _, _ in issues]
    assert "no_whitespace_in_keys" in rules


def test_lint_unquoted_special_chars():
    issues = lint_env({"SECRET": "pa$$word"})
    rules = [r for r, _, _ in issues]
    assert "no_unquoted_special_chars" in rules


def test_lint_quoted_value_no_issue():
    issues = lint_env({"SECRET": '"pa$$word"'})
    rules = [r for r, _, _ in issues]
    assert "no_unquoted_special_chars" not in rules


def test_lint_clean_env():
    issues = lint_env({"FOO": "bar", "BAZ": "123"})
    assert issues == []


def test_lint_lines_duplicate_keys():
    lines = ["FOO=bar\n", "BAZ=1\n", "FOO=other\n"]
    issues = lint_lines(lines)
    rules = [r for r, _, _ in issues]
    assert "no_duplicate_keys" in rules


def test_lint_lines_no_duplicates():
    lines = ["FOO=bar\n", "BAZ=1\n"]
    issues = lint_lines(lines)
    assert issues == []


def test_format_lint_results_no_issues():
    assert format_lint_results([]) == "No issues found."


def test_format_lint_results_with_issues():
    issues = [("no_empty_values", "FOO", "Key 'FOO' has an empty value.")]
    result = format_lint_results(issues)
    assert "no_empty_values" in result
    assert "FOO" in result


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_check_clean_file(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=123\n")
    result = runner.invoke(lint_cli, ["check", str(env_file)])
    assert result.exit_code == 0
    assert "No issues found" in result.output


def test_cli_check_with_issues(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=\n")
    result = runner.invoke(lint_cli, ["check", str(env_file)])
    assert "no_empty_values" in result.output


def test_cli_check_strict_exits_nonzero(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=\n")
    result = runner.invoke(lint_cli, ["check", str(env_file), "--strict"])
    assert result.exit_code != 0


def test_cli_list_rules(runner):
    result = runner.invoke(lint_cli, ["rules"])
    assert result.exit_code == 0
    assert "no_empty_values" in result.output

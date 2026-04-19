"""Tests for envoy/template.py and cli_template.py."""
import os
import pytest
from click.testing import CliRunner
from envoy.template import render_template, parse_template, missing_variables, render_template_file
from envoy.cli_template import template_cli


# --- Unit tests for template.py ---

def test_render_simple_substitution():
    result = render_template("DB_HOST={{ HOST }}", {"HOST": "localhost"})
    assert result == "DB_HOST=localhost"


def test_render_default_used_when_missing():
    result = render_template("PORT={{ PORT:-5432 }}", {})
    assert result == "PORT=5432"


def test_render_value_overrides_default():
    result = render_template("PORT={{ PORT:-5432 }}", {"PORT": "3306"})
    assert result == "PORT=3306"


def test_render_strict_raises_on_missing():
    with pytest.raises(KeyError, match="SECRET"):
        render_template("SECRET={{ SECRET }}", {}, strict=True)


def test_render_non_strict_leaves_placeholder():
    result = render_template("X={{ UNKNOWN }}", {}, strict=False)
    assert "UNKNOWN" in result


def test_parse_template_finds_vars():
    tmpl = "A={{ FOO }} B={{ BAR:-baz }}"
    vars_ = parse_template(tmpl)
    assert ("FOO", None) in vars_
    assert ("BAR", "baz") in vars_


def test_missing_variables_detects_missing():
    tmpl = "A={{ FOO }} B={{ BAR:-default }}"
    missing = missing_variables(tmpl, {})
    assert "FOO" in missing
    assert "BAR" not in missing


def test_render_template_file(tmp_path):
    tpl = tmp_path / "app.env.tpl"
    tpl.write_text("DB={{ DB_NAME:-mydb }}\nHOST={{ HOST }}\n")
    out = tmp_path / "app.env"
    render_template_file(str(tpl), str(out), {"HOST": "prod-server"})
    content = out.read_text()
    assert "DB=mydb" in content
    assert "HOST=prod-server" in content


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_render(runner, tmp_path):
    tpl = tmp_path / "t.env.tpl"
    tpl.write_text("KEY={{ KEY:-hello }}\n")
    out = tmp_path / "out.env"
    result = runner.invoke(template_cli, ["render", str(tpl), str(out)])
    assert result.exit_code == 0
    assert out.read_text() == "KEY=hello\n"


def test_cli_render_strict_missing(runner, tmp_path):
    tpl = tmp_path / "t.env.tpl"
    tpl.write_text("SECRET={{ SECRET }}\n")
    out = tmp_path / "out.env"
    result = runner.invoke(template_cli, ["render", "--strict", str(tpl), str(out)])
    assert result.exit_code != 0


def test_cli_check_satisfied(runner, tmp_path):
    tpl = tmp_path / "t.env.tpl"
    tpl.write_text("A={{ A:-default }}\n")
    result = runner.invoke(template_cli, ["check", str(tpl)])
    assert result.exit_code == 0
    assert "satisfied" in result.output


def test_cli_check_missing(runner, tmp_path):
    tpl = tmp_path / "t.env.tpl"
    tpl.write_text("A={{ REQUIRED_VAR }}\n")
    result = runner.invoke(template_cli, ["check", str(tpl)])
    assert result.exit_code == 1
    assert "REQUIRED_VAR" in result.output

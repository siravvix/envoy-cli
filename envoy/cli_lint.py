"""CLI commands for linting .env files."""

import click
from envoy.env_file import read_env_file
from envoy.lint import lint_env, lint_lines, format_lint_results


@click.group(name="lint")
def lint_cli():
    """Lint .env files for common issues."""
    pass


@lint_cli.command(name="check")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--rule", multiple=True, help="Specific rules to apply (default: all).")
@click.option("--strict", is_flag=True, default=False, help="Exit with error code if issues found.")
def check(env_file, rule, strict):
    """Check an .env file for lint issues."""
    rules = list(rule) if rule else None

    with open(env_file, "r") as f:
        raw_lines = f.readlines()

    data = read_env_file(env_file)

    issues = lint_lines(raw_lines, rules=rules)
    issues += lint_env(data, rules=rules)

    if issues:
        click.echo(f"Issues found in {env_file}:")
        click.echo(format_lint_results(issues))
        if strict:
            raise SystemExit(1)
    else:
        click.echo(f"{env_file}: No issues found.")


@lint_cli.command(name="rules")
def list_rules():
    """List all available lint rules."""
    from envoy.lint import LINT_RULES
    click.echo("Available lint rules:")
    for r in LINT_RULES:
        click.echo(f"  - {r}")

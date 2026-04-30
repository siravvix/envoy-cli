"""CLI commands for deprecation tracking."""

import click

from envoy.deprecate import (
    deprecate_key,
    undeprecate_key,
    load_deprecations,
    check_env_for_deprecated,
    format_deprecation_results,
)
from envoy.env_file import read_env_file


@click.group(name="deprecate")
def deprecate_cli():
    """Track and check deprecated .env keys."""


@deprecate_cli.command(name="add")
@click.argument("key")
@click.option("--reason", default="", help="Why this key is deprecated.")
@click.option("--replacement", default=None, help="Suggested replacement key.")
@click.option("--profile", default="default", show_default=True)
def add_cmd(key, reason, replacement, profile):
    """Mark a key as deprecated."""
    try:
        deprecate_key(key, reason=reason, replacement=replacement, profile=profile)
        click.echo(f"Marked '{key}' as deprecated.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@deprecate_cli.command(name="remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def remove_cmd(key, profile):
    """Remove deprecation mark from a key."""
    removed = undeprecate_key(key, profile=profile)
    if removed:
        click.echo(f"Removed deprecation for '{key}'.")
    else:
        click.echo(f"Key '{key}' was not marked as deprecated.", err=True)
        raise SystemExit(1)


@deprecate_cli.command(name="list")
@click.option("--profile", default="default", show_default=True)
def list_cmd(profile):
    """List all deprecated keys for a profile."""
    data = load_deprecations(profile)
    if not data:
        click.echo("No deprecated keys.")
        return
    for key, meta in data.items():
        line = f"  {key}"
        if meta.get("reason"):
            line += f" — {meta['reason']}"
        if meta.get("replacement"):
            line += f" (use '{meta['replacement']}' instead)"
        click.echo(line)


@deprecate_cli.command(name="check")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--profile", default="default", show_default=True)
def check_cmd(env_file, profile):
    """Check an .env file for deprecated keys."""
    env = read_env_file(env_file)
    results = check_env_for_deprecated(env, profile=profile)
    output = format_deprecation_results(results)
    click.echo(output)
    if results:
        raise SystemExit(1)

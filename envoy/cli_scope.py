"""CLI commands for scope management."""

import click
from envoy import scope as scope_mod
from envoy.env_file import read_env_file


@click.group("scope")
def scope_cli():
    """Manage environment variable scopes."""


@scope_cli.command("add")
@click.argument("scope_name")
@click.argument("key")
def add_cmd(scope_name, key):
    """Add KEY to SCOPE_NAME."""
    try:
        scope_mod.add_key_to_scope(scope_name, key)
        click.echo(f"Added '{key}' to scope '{scope_name}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@scope_cli.command("remove")
@click.argument("scope_name")
@click.argument("key")
def remove_cmd(scope_name, key):
    """Remove KEY from SCOPE_NAME."""
    removed = scope_mod.remove_key_from_scope(scope_name, key)
    if removed:
        click.echo(f"Removed '{key}' from scope '{scope_name}'.")
    else:
        click.echo(f"Key '{key}' not found in scope '{scope_name}'.")


@scope_cli.command("list")
@click.argument("scope_name", required=False)
def list_cmd(scope_name):
    """List all scopes or keys within SCOPE_NAME."""
    if scope_name:
        keys = scope_mod.get_scope_keys(scope_name)
        if not keys:
            click.echo(f"Scope '{scope_name}' is empty or does not exist.")
        else:
            for k in keys:
                click.echo(k)
    else:
        scopes = scope_mod.list_scopes()
        if not scopes:
            click.echo("No scopes defined.")
        else:
            for s in scopes:
                click.echo(s)


@scope_cli.command("filter")
@click.argument("scope_name")
@click.argument("env_file", type=click.Path(exists=True))
def filter_cmd(scope_name, env_file):
    """Print only keys from ENV_FILE that belong to SCOPE_NAME."""
    env = read_env_file(env_file)
    filtered = scope_mod.filter_env_by_scope(env, scope_name)
    if not filtered:
        click.echo(f"No matching keys for scope '{scope_name}'.")
    else:
        for k, v in filtered.items():
            click.echo(f"{k}={v}")


@scope_cli.command("delete")
@click.argument("scope_name")
def delete_cmd(scope_name):
    """Delete an entire scope."""
    deleted = scope_mod.delete_scope(scope_name)
    if deleted:
        click.echo(f"Scope '{scope_name}' deleted.")
    else:
        click.echo(f"Scope '{scope_name}' not found.")

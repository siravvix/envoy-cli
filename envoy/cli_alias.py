"""CLI commands for alias management."""

from __future__ import annotations

import click

from envoy.alias import (
    add_alias,
    format_aliases,
    list_aliases,
    remove_alias,
    resolve_alias,
)


@click.group("alias")
def alias_cli() -> None:
    """Manage short aliases for env keys."""


@alias_cli.command("add")
@click.argument("alias")
@click.argument("key")
def add_cmd(alias: str, key: str) -> None:
    """Add or update ALIAS pointing to KEY."""
    try:
        add_alias(alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' saved.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@alias_cli.command("remove")
@click.argument("alias")
def remove_cmd(alias: str) -> None:
    """Remove an existing ALIAS."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@alias_cli.command("list")
def list_cmd() -> None:
    """List all defined aliases."""
    aliases = list_aliases()
    click.echo(format_aliases(aliases))


@alias_cli.command("resolve")
@click.argument("alias")
def resolve_cmd(alias: str) -> None:
    """Print the key that ALIAS maps to."""
    key = resolve_alias(alias)
    if key is None:
        raise click.ClickException(f"Alias '{alias}' not found.")
    click.echo(key)

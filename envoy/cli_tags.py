"""CLI commands for managing profile tags."""

from __future__ import annotations

import click

from envoy.tags import (
    add_tag,
    remove_tag,
    get_tags,
    profiles_with_tag,
    clear_profile_tags,
)


@click.group("tags")
def tags_cli():
    """Manage tags for env profiles."""


@tags_cli.command("add")
@click.argument("profile")
@click.argument("tag")
def add_cmd(profile: str, tag: str):
    """Add TAG to PROFILE."""
    add_tag(profile, tag)
    click.echo(f"Tag '{tag}' added to profile '{profile}'.")


@tags_cli.command("remove")
@click.argument("profile")
@click.argument("tag")
def remove_cmd(profile: str, tag: str):
    """Remove TAG from PROFILE."""
    removed = remove_tag(profile, tag)
    if removed:
        click.echo(f"Tag '{tag}' removed from profile '{profile}'.")
    else:
        click.echo(f"Tag '{tag}' not found on profile '{profile}'.")
        raise SystemExit(1)


@tags_cli.command("list")
@click.argument("profile")
def list_cmd(profile: str):
    """List all tags for PROFILE."""
    tags = get_tags(profile)
    if not tags:
        click.echo(f"No tags for profile '{profile}'.")
    else:
        for tag in tags:
            click.echo(tag)


@tags_cli.command("find")
@click.argument("tag")
def find_cmd(tag: str):
    """Find all profiles that have TAG."""
    profiles = profiles_with_tag(tag)
    if not profiles:
        click.echo(f"No profiles found with tag '{tag}'.")
    else:
        for profile in profiles:
            click.echo(profile)


@tags_cli.command("clear")
@click.argument("profile")
def clear_cmd(profile: str):
    """Remove all tags from PROFILE."""
    clear_profile_tags(profile)
    click.echo(f"All tags cleared from profile '{profile}'.")

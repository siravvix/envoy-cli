"""CLI commands for shell completion support."""

import click

from envoy.completion import (
    get_env_keys,
    get_profile_names,
    generate_bash_completion,
    generate_zsh_completion,
)


@click.group("complete")
def completion_cli():
    """Shell completion utilities."""
    pass


@completion_cli.command("install")
@click.argument("shell", type=click.Choice(["bash", "zsh"]), default="bash")
@click.option("--name", default="envoy", help="CLI script name")
def install(shell: str, name: str):
    """Print shell completion script to stdout.

    Usage:
      eval "$(envoy complete install bash)"
    """
    if shell == "bash":
        click.echo(generate_bash_completion(name))
    elif shell == "zsh":
        click.echo(generate_zsh_completion(name))


@completion_cli.command("keys")
@click.argument("filepath")
def keys(filepath: str):
    """List all keys in a .env file (for completion use)."""
    result = get_env_keys(filepath)
    if result:
        click.echo("\n".join(result))
    else:
        click.echo("", err=True)


@completion_cli.command("profiles")
def profiles():
    """List all saved profiles (for completion use)."""
    result = get_profile_names()
    if result:
        click.echo("\n".join(result))
    else:
        click.echo("", err=True)

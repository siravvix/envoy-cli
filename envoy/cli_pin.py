"""CLI commands for pinning/unpinning env keys."""

import click
from envoy.pin import pin_key, unpin_key, list_pinned, load_pins


@click.group("pin")
def pin_cli():
    """Pin keys to protect them from being overwritten."""
    pass


@pin_cli.command("add")
@click.argument("env_file")
@click.argument("key")
@click.option("--reason", "-r", default="", help="Optional reason for pinning.")
def add_cmd(env_file: str, key: str, reason: str):
    """Pin KEY in ENV_FILE."""
    pin_key(env_file, key, reason=reason or None)
    click.echo(f"Pinned '{key}'" + (f" — {reason}" if reason else ""))


@pin_cli.command("remove")
@click.argument("env_file")
@click.argument("key")
def remove_cmd(env_file: str, key: str):
    """Unpin KEY in ENV_FILE."""
    removed = unpin_key(env_file, key)
    if removed:
        click.echo(f"Unpinned '{key}'.")
    else:
        click.echo(f"Key '{key}' was not pinned.", err=True)
        raise SystemExit(1)


@pin_cli.command("list")
@click.argument("env_file")
def list_cmd(env_file: str):
    """List all pinned keys in ENV_FILE."""
    keys = list_pinned(env_file)
    if not keys:
        click.echo("No keys are pinned.")
        return
    pins = load_pins(env_file)
    for key in keys:
        reason = pins[key].get("reason", "")
        suffix = f"  # {reason}" if reason else ""
        click.echo(f"  {key}{suffix}")

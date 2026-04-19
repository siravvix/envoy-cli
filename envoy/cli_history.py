"""CLI commands for viewing and restoring env file history."""
import click
from envoy.history import read_history, clear_history, get_snapshot
from envoy.env_file import write_env_file


@click.group(name="history")
def history_cli():
    """Manage env file change history."""


@history_cli.command("list")
@click.argument("profile")
def list_history(profile):
    """List history snapshots for a profile."""
    entries = read_history(profile)
    if not entries:
        click.echo(f"No history found for profile '{profile}'.")
        return
    for i, entry in enumerate(entries):
        msg = entry.get("message") or "(no message)"
        click.echo(f"[{i}] {entry['timestamp']}  {msg}")


@history_cli.command("show")
@click.argument("profile")
@click.argument("index", type=int)
def show_snapshot(profile, index):
    """Show env variables at a specific history index."""
    entry = get_snapshot(profile, index)
    if entry is None:
        click.echo(f"Snapshot {index} not found for profile '{profile}'.", err=True)
        raise SystemExit(1)
    for k, v in entry["env"].items():
        click.echo(f"{k}={v}")


@history_cli.command("restore")
@click.argument("profile")
@click.argument("index", type=int)
@click.argument("output")
def restore_snapshot(profile, index, output):
    """Restore a snapshot to an env file."""
    entry = get_snapshot(profile, index)
    if entry is None:
        click.echo(f"Snapshot {index} not found for profile '{profile}'.", err=True)
        raise SystemExit(1)
    write_env_file(output, entry["env"])
    click.echo(f"Restored snapshot {index} to {output}")


@history_cli.command("clear")
@click.argument("profile")
def clear(profile):
    """Clear all history for a profile."""
    clear_history(profile)
    click.echo(f"History cleared for profile '{profile}'.")

"""CLI commands for backup and restore of .env files."""

import click
from envoy.backup import create_backup, list_backups, restore_backup, delete_backup


@click.group("backup")
def backup_cli():
    """Backup and restore .env files."""


@backup_cli.command("create")
@click.argument("file", type=click.Path(exists=True))
@click.option("--label", "-l", required=True, help="Backup label (e.g. profile name or env name).")
@click.option("--note", "-n", default="", help="Optional note for this backup.")
def create_cmd(file, label, note):
    """Create a backup of FILE under LABEL."""
    entry = create_backup(file, label, note=note)
    click.echo(f"Backup created at {entry['timestamp']}")
    if note:
        click.echo(f"Note: {note}")


@backup_cli.command("list")
@click.option("--label", "-l", required=True, help="Backup label to list.")
def list_cmd(label):
    """List all backups for LABEL."""
    entries = list_backups(label)
    if not entries:
        click.echo(f"No backups found for label '{label}'.")
        return
    for e in entries:
        note_str = f"  # {e['note']}" if e.get("note") else ""
        click.echo(f"{e['timestamp']}{note_str}")


@backup_cli.command("restore")
@click.option("--label", "-l", required=True, help="Backup label.")
@click.option("--timestamp", "-t", required=True, help="Timestamp of the backup to restore.")
@click.argument("dest", type=click.Path())
def restore_cmd(label, timestamp, dest):
    """Restore a backup to DEST."""
    try:
        restore_backup(label, timestamp, dest)
        click.echo(f"Restored backup from {timestamp} to {dest}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@backup_cli.command("delete")
@click.option("--label", "-l", required=True, help="Backup label.")
@click.option("--timestamp", "-t", required=True, help="Timestamp of the backup to delete.")
def delete_cmd(label, timestamp):
    """Delete a specific backup entry."""
    try:
        delete_backup(label, timestamp)
        click.echo(f"Deleted backup {timestamp} from label '{label}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

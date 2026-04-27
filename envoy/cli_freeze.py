"""CLI commands for freezing/unfreezing .env files."""

import click
from envoy.freeze import freeze_file, unfreeze_file, is_frozen, list_frozen


@click.group("freeze")
def freeze_cli():
    """Freeze or unfreeze .env files to prevent accidental modification."""


@freeze_cli.command("lock")
@click.argument("filepath", type=click.Path(exists=True))
def lock_cmd(filepath: str):
    """Freeze a .env file."""
    try:
        freeze_file(filepath)
        click.echo(f"Frozen: {filepath}")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@freeze_cli.command("unlock")
@click.argument("filepath", type=click.Path())
def unlock_cmd(filepath: str):
    """Unfreeze a .env file."""
    removed = unfreeze_file(filepath)
    if removed:
        click.echo(f"Unfrozen: {filepath}")
    else:
        click.echo(f"File was not frozen: {filepath}")


@freeze_cli.command("status")
@click.argument("filepath", type=click.Path())
def status_cmd(filepath: str):
    """Check if a .env file is frozen."""
    if is_frozen(filepath):
        click.echo(f"frozen: {filepath}")
    else:
        click.echo(f"not frozen: {filepath}")


@freeze_cli.command("list")
def list_cmd():
    """List all frozen .env files."""
    frozen = list_frozen()
    if not frozen:
        click.echo("No files are currently frozen.")
    else:
        for path in frozen:
            click.echo(path)

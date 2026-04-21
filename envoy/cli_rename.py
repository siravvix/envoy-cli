"""CLI commands for renaming and copying env keys."""

import click
from envoy.rename import rename_key_in_file, copy_key_in_file


@click.group(name="rename")
def rename_cli():
    """Rename or copy keys within a .env file."""


@rename_cli.command(name="key")
@click.argument("file", type=click.Path(exists=True))
@click.argument("old_key")
@click.argument("new_key")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite new_key if it already exists.",
)
def rename_key_cmd(file: str, old_key: str, new_key: str, overwrite: bool):
    """Rename OLD_KEY to NEW_KEY in FILE."""
    try:
        rename_key_in_file(file, old_key, new_key, overwrite=overwrite)
        click.echo(f"Renamed '{old_key}' -> '{new_key}' in {file}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rename_cli.command(name="copy")
@click.argument("file", type=click.Path(exists=True))
@click.argument("src_key")
@click.argument("dest_key")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite dest_key if it already exists.",
)
def copy_key_cmd(file: str, src_key: str, dest_key: str, overwrite: bool):
    """Copy SRC_KEY to DEST_KEY in FILE."""
    try:
        copy_key_in_file(file, src_key, dest_key, overwrite=overwrite)
        click.echo(f"Copied '{src_key}' -> '{dest_key}' in {file}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

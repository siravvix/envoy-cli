"""CLI commands for importing and exporting profiles."""
import click
from envoy.import_export_profile import (
    export_profile, import_profile, export_all_profiles, import_all_profiles
)


@click.group(name="transfer")
def transfer_cli():
    """Import and export profile archives."""
    pass


@transfer_cli.command("export")
@click.argument("profile")
@click.argument("output")
def export_cmd(profile, output):
    """Export a single PROFILE to OUTPUT archive."""
    try:
        export_profile(profile, output)
        click.echo(f"Exported profile '{profile}' to {output}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@transfer_cli.command("import")
@click.argument("archive")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing profile.")
def import_cmd(archive, overwrite):
    """Import a profile from ARCHIVE."""
    try:
        name = import_profile(archive, overwrite=overwrite)
        click.echo(f"Imported profile '{name}'")
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@transfer_cli.command("export-all")
@click.argument("output")
def export_all_cmd(output):
    """Export all profiles to OUTPUT archive."""
    names = export_all_profiles(output)
    click.echo(f"Exported {len(names)} profile(s) to {output}: {', '.join(names)}")


@transfer_cli.command("import-all")
@click.argument("archive")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing profiles.")
def import_all_cmd(archive, overwrite):
    """Import all profiles from ARCHIVE."""
    imported = import_all_profiles(archive, overwrite=overwrite)
    if imported:
        click.echo(f"Imported {len(imported)} profile(s): {', '.join(imported)}")
    else:
        click.echo("No profiles imported (all already exist, use --overwrite to replace).")

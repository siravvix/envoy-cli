"""CLI commands for key rotation."""

import click
from envoy.rotate import rotate_key, rotate_profile_key


@click.group("rotate")
def rotate_cli():
    """Rotate encryption keys for env files or profiles."""


@rotate_cli.command("file")
@click.argument("filepath")
@click.option("--old-password", prompt=True, hide_input=True, help="Current password")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New password")
def rotate_file(filepath, old_password, new_password):
    """Re-encrypt FILE with a new password."""
    try:
        result = rotate_key(filepath, old_password, new_password)
        click.echo(f"✓ Rotated {result['keys_rotated']} key(s) in '{filepath}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rotate_cli.command("profile")
@click.argument("profile_name")
@click.option("--old-password", prompt=True, hide_input=True, help="Current password")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New password")
def rotate_profile(profile_name, old_password, new_password):
    """Re-encrypt a stored PROFILE with a new password."""
    try:
        result = rotate_profile_key(profile_name, old_password, new_password)
        click.echo(f"✓ Rotated {result['keys_rotated']} key(s) in profile '{profile_name}'.")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

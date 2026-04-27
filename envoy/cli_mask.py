"""CLI commands for masking sensitive .env values."""

import click
from envoy.env_file import read_env_file
from envoy.mask import mask_env, list_masked_keys

MODES = ["partial", "full", "length"]


@click.group(name="mask")
def mask_cli():
    """Mask or inspect sensitive values in .env files."""


@mask_cli.command(name="show")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--mode",
    default="partial",
    type=click.Choice(MODES),
    show_default=True,
    help="Masking mode.",
)
@click.option(
    "--key",
    "keys",
    multiple=True,
    help="Additional keys to mask (can be repeated).",
)
@click.option(
    "--no-auto",
    is_flag=True,
    default=False,
    help="Disable auto-detection of sensitive keys.",
)
@click.option("--char", default="*", show_default=True, help="Mask character.")
def show_cmd(env_file, mode, keys, no_auto, char):
    """Display .env file with sensitive values masked."""
    env = read_env_file(env_file)
    masked = mask_env(
        env,
        mode=mode,
        keys=list(keys),
        auto_detect=not no_auto,
        char=char,
    )
    for k, v in masked.items():
        click.echo(f"{k}={v}")


@mask_cli.command(name="list")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--key",
    "keys",
    multiple=True,
    help="Additional keys to include in check.",
)
@click.option(
    "--no-auto",
    is_flag=True,
    default=False,
    help="Disable auto-detection of sensitive keys.",
)
def list_cmd(env_file, keys, no_auto):
    """List keys that would be masked in an .env file."""
    env = read_env_file(env_file)
    sensitive = list_masked_keys(env, keys=list(keys), auto_detect=not no_auto)
    if not sensitive:
        click.echo("No sensitive keys detected.")
        return
    click.echo(f"Sensitive keys ({len(sensitive)}):")
    for k in sensitive:
        click.echo(f"  {k}")

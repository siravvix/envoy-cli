"""CLI commands for formatting .env files."""

import click
from envoy.env_file import read_env_file, write_env_file
from envoy.fmt import format_env


@click.group("fmt")
def fmt_cli():
    """Format and normalize .env files."""


@fmt_cli.command("apply")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--sort", is_flag=True, default=False, help="Sort keys alphabetically.")
@click.option("--align", is_flag=True, default=False, help="Align values at same column.")
@click.option("--normalize", is_flag=True, default=False, help="Normalize quoting of values.")
@click.option("--inplace", "-i", is_flag=True, default=False, help="Write changes back to file.")
@click.option("--output", "-o", type=click.Path(), default=None, help="Write output to this file.")
def apply_cmd(env_file, sort, align, normalize, inplace, output):
    """Apply formatting rules to an .env file."""
    env = read_env_file(env_file)
    formatted = format_env(env, sort=sort, align=align, normalize=normalize)

    if inplace:
        with open(env_file, "w") as f:
            f.write(formatted)
        click.echo(f"Formatted {env_file} in place.")
    elif output:
        with open(output, "w") as f:
            f.write(formatted)
        click.echo(f"Formatted output written to {output}.")
    else:
        click.echo(formatted, nl=False)


@fmt_cli.command("check")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--sort", is_flag=True, default=False)
@click.option("--align", is_flag=True, default=False)
@click.option("--normalize", is_flag=True, default=False)
def check_cmd(env_file, sort, align, normalize):
    """Check if a file is already formatted; exit 1 if not."""
    env = read_env_file(env_file)
    formatted = format_env(env, sort=sort, align=align, normalize=normalize)
    with open(env_file) as f:
        current = f.read()
    if current == formatted:
        click.echo(f"{env_file} is already formatted.")
    else:
        click.echo(f"{env_file} is NOT formatted. Run `envoy fmt apply` to fix.", err=True)
        raise SystemExit(1)

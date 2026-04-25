"""CLI commands for variable interpolation."""

import click

from envoy.env_file import read_env_file, write_env_file
from envoy.interpolate import InterpolationError, interpolate_env, unresolved_references


@click.group(name="interpolate")
def interpolate_cli() -> None:
    """Interpolate ${VAR} references inside .env files."""


@interpolate_cli.command("apply")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Write result to this file (default: stdout).")
@click.option("--no-os-env", is_flag=True, default=False, help="Do not fall back to OS environment variables.")
@click.option("--strict", is_flag=True, default=False, help="Fail on unresolved references.")
def apply_cmd(env_file: str, output: str | None, no_os_env: bool, strict: bool) -> None:
    """Resolve all variable references in ENV_FILE and print or save the result."""
    env = read_env_file(env_file)
    try:
        resolved = interpolate_env(env, use_os_env=not no_os_env, strict=strict)
    except InterpolationError as exc:
        raise click.ClickException(str(exc)) from exc

    lines = [f"{k}={v}" for k, v in resolved.items()]
    result = "\n".join(lines) + "\n"

    if output:
        with open(output, "w") as fh:
            fh.write(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result, nl=False)


@interpolate_cli.command("check")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--no-os-env", is_flag=True, default=False, help="Do not fall back to OS environment variables.")
def check_cmd(env_file: str, no_os_env: bool) -> None:
    """Report any unresolved variable references in ENV_FILE."""
    env = read_env_file(env_file)
    missing = unresolved_references(env, use_os_env=not no_os_env)

    if not missing:
        click.echo("All references resolved.")
        return

    click.echo("Unresolved references found:", err=True)
    for key, refs in missing.items():
        click.echo(f"  {key}: {', '.join(refs)}", err=True)
    raise SystemExit(1)

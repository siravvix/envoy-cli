"""CLI commands for injecting .env variables into a subprocess."""

from __future__ import annotations

import sys

import click

from envoy.inject import inject_and_run, preview_env, InjectError


@click.group("inject")
def inject_cli() -> None:
    """Inject .env variables into a command's environment."""


@inject_cli.command("run")
@click.option("--env-file", "-e", required=True, help="Path to the .env file.")
@click.option("--password", "-p", default=None, help="Decryption password (if encrypted).")
@click.option("--interpolate", "-i", is_flag=True, default=False, help="Interpolate variable references.")
@click.option("--no-inherit", is_flag=True, default=False, help="Do not inherit the current OS environment.")
@click.argument("command", nargs=-1, required=True)
def run_cmd(
    env_file: str,
    password: str | None,
    interpolate: bool,
    no_inherit: bool,
    command: tuple,
) -> None:
    """Run COMMAND with variables from ENV_FILE injected."""
    try:
        code = inject_and_run(
            env_path=env_file,
            command=list(command),
            password=password,
            interpolate=interpolate,
            inherit_os_env=not no_inherit,
        )
        sys.exit(code)
    except InjectError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@inject_cli.command("preview")
@click.option("--env-file", "-e", required=True, help="Path to the .env file.")
@click.option("--password", "-p", default=None, help="Decryption password (if encrypted).")
@click.option("--interpolate", "-i", is_flag=True, default=False, help="Interpolate variable references.")
@click.option("--inherit", is_flag=True, default=False, help="Include current OS environment in preview.")
def preview_cmd(
    env_file: str,
    password: str | None,
    interpolate: bool,
    inherit: bool,
) -> None:
    """Preview the environment that would be injected (does not run a command)."""
    try:
        env = preview_env(
            env_path=env_file,
            password=password,
            interpolate=interpolate,
            inherit_os_env=inherit,
        )
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    for key, value in sorted(env.items()):
        click.echo(f"{key}={value}")

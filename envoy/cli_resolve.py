"""CLI commands for resolving .env keys across multiple files or profiles."""

import click
from envoy.resolve import resolve_files, resolve_all, resolve_missing, format_resolve_trace, ResolveError
from envoy.env_file import parse_env, read_env_file


@click.group("resolve")
def resolve_cli():
    """Resolve variable values across multiple .env sources."""


@resolve_cli.command("get")
@click.argument("key")
@click.argument("files", nargs=-1, required=True)
def get_cmd(key: str, files: tuple):
    """Get the resolved value of KEY from one or more FILES (last wins)."""
    try:
        value = resolve_files(key, list(files))
    except ResolveError as e:
        raise click.ClickException(str(e))

    if value is None:
        raise click.ClickException(f"Key '{key}' not found in any source file.")
    click.echo(value)


@resolve_cli.command("trace")
@click.argument("key")
@click.argument("files", nargs=-1, required=True)
def trace_cmd(key: str, files: tuple):
    """Show which source files define KEY and which value wins."""
    named_sources = []
    for path in files:
        try:
            content = read_env_file(path)
            named_sources.append((path, parse_env(content)))
        except FileNotFoundError:
            raise click.ClickException(f"File not found: {path}")

    click.echo(format_resolve_trace(key, named_sources))


@resolve_cli.command("missing")
@click.argument("keys", nargs=-1, required=True)
@click.option("--file", "-f", "files", multiple=True, required=True, help="Source .env files")
def missing_cmd(keys: tuple, files: tuple):
    """List which KEYS are missing across all provided source FILES."""
    sources = []
    for path in files:
        try:
            content = read_env_file(path)
            sources.append(parse_env(content))
        except FileNotFoundError:
            raise click.ClickException(f"File not found: {path}")

    absent = resolve_missing(list(keys), sources)
    if not absent:
        click.echo("All keys are defined.")
    else:
        for k in absent:
            click.echo(f"MISSING: {k}")

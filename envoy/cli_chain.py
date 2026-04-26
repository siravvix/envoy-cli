"""CLI commands for chaining .env files with precedence."""

import click
from envoy.chain import load_chain, chain_sources, chain_conflicts, format_chain_sources


@click.group(name="chain")
def chain_cli():
    """Chain multiple .env files with override precedence."""


@chain_cli.command(name="show")
@click.argument("files", nargs=-1, required=True)
@click.option("--with-source", is_flag=True, help="Show which file each key comes from.")
def show_cmd(files, with_source):
    """Merge FILES in order and display the result."""
    try:
        if with_source:
            sources = chain_sources(list(files))
            click.echo(format_chain_sources(sources))
        else:
            merged = load_chain(list(files))
            if not merged:
                click.echo("(empty)")
            else:
                for key, value in sorted(merged.items()):
                    click.echo(f"{key}={value}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@chain_cli.command(name="conflicts")
@click.argument("files", nargs=-1, required=True)
def conflicts_cmd(files):
    """Show keys that differ across FILES."""
    try:
        found = chain_conflicts(list(files))
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))

    if not found:
        click.echo("No conflicts found.")
        return

    for key, occurrences in sorted(found.items()):
        click.echo(f"[{key}]")
        for value, src in occurrences:
            click.echo(f"  {src}: {value}")


@chain_cli.command(name="get")
@click.argument("files", nargs=-1, required=True)
@click.option("-k", "--key", required=True, help="Key to look up after merging.")
def get_cmd(files, key):
    """Look up a single KEY after merging FILES."""
    try:
        merged = load_chain(list(files))
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))

    if key not in merged:
        raise click.ClickException(f"Key '{key}' not found.")
    click.echo(merged[key])

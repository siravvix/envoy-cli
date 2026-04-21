"""CLI commands for searching env files."""
import click
from envoy.env_file import read_env_file
from envoy.search import search_keys, search_values, search_any, filter_by_prefix, format_search_results


@click.group(name="search")
def search_cli():
    """Search and filter .env file entries."""
    pass


def _load_env_file(file):
    """Load an env file, raising a ClickException if not found."""
    try:
        return read_env_file(file)
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {file}")


@search_cli.command()
@click.argument("pattern")
@click.option("--file", "-f", default=".env", show_default=True, help="Path to .env file.")
@click.option("--target", "-t", type=click.Choice(["key", "value", "any"]), default="any", show_default=True)
@click.option("--case-sensitive", is_flag=True, default=False, help="Enable case-sensitive matching.")
def find(pattern, file, target, case_sensitive):
    """Search entries by PATTERN in keys, values, or both."""
    env = _load_env_file(file)

    if target == "key":
        results = search_keys(env, pattern, case_sensitive)
    elif target == "value":
        results = search_values(env, pattern, case_sensitive)
    else:
        results = search_any(env, pattern, case_sensitive)

    click.echo(format_search_results(results, pattern))


@search_cli.command()
@click.argument("prefix")
@click.option("--file", "-f", default=".env", show_default=True, help="Path to .env file.")
def prefix(prefix, file):
    """Filter entries whose keys start with PREFIX."""
    env = _load_env_file(file)

    results = filter_by_prefix(env, prefix)
    click.echo(format_search_results(results))

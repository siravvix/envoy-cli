"""CLI commands for reordering keys in .env files."""
import click
from envoy.env_file import read_env_file, write_env_file
from envoy.reorder import reorder_by_list, reorder_by_prefix_priority, move_to_top, move_to_bottom, ReorderError, format_reorder_diff


@click.group(name="reorder")
def reorder_cli():
    """Reorder keys in a .env file."""


@reorder_cli.command(name="by-list")
@click.argument("env_file")
@click.argument("keys", nargs=-1, required=True)
@click.option("--inplace", is_flag=True, help="Write changes back to the file.")
@click.option("--no-append", is_flag=True, help="Omit keys not in the list.")
def by_list_cmd(env_file, keys, inplace, no_append):
    """Reorder keys by an explicit ordered list."""
    env = read_env_file(env_file)
    reordered = reorder_by_list(env, list(keys), append_remaining=not no_append)
    diff = format_reorder_diff(env, reordered)
    click.echo(diff)
    if inplace:
        write_env_file(env_file, reordered)
        click.echo(f"Written to {env_file}")


@reorder_cli.command(name="by-prefix")
@click.argument("env_file")
@click.argument("prefixes", nargs=-1, required=True)
@click.option("--sep", default="_", show_default=True, help="Prefix separator.")
@click.option("--inplace", is_flag=True, help="Write changes back to the file.")
def by_prefix_cmd(env_file, prefixes, sep, inplace):
    """Reorder keys by prefix priority."""
    env = read_env_file(env_file)
    reordered = reorder_by_prefix_priority(env, list(prefixes), sep=sep)
    diff = format_reorder_diff(env, reordered)
    click.echo(diff)
    if inplace:
        write_env_file(env_file, reordered)
        click.echo(f"Written to {env_file}")


@reorder_cli.command(name="top")
@click.argument("env_file")
@click.argument("keys", nargs=-1, required=True)
@click.option("--inplace", is_flag=True, help="Write changes back to the file.")
def top_cmd(env_file, keys, inplace):
    """Move specified keys to the top of the file."""
    env = read_env_file(env_file)
    try:
        reordered = move_to_top(env, list(keys))
    except ReorderError as e:
        raise click.ClickException(str(e))
    diff = format_reorder_diff(env, reordered)
    click.echo(diff)
    if inplace:
        write_env_file(env_file, reordered)
        click.echo(f"Written to {env_file}")


@reorder_cli.command(name="bottom")
@click.argument("env_file")
@click.argument("keys", nargs=-1, required=True)
@click.option("--inplace", is_flag=True, help="Write changes back to the file.")
def bottom_cmd(env_file, keys, inplace):
    """Move specified keys to the bottom of the file."""
    env = read_env_file(env_file)
    try:
        reordered = move_to_bottom(env, list(keys))
    except ReorderError as e:
        raise click.ClickException(str(e))
    diff = format_reorder_diff(env, reordered)
    click.echo(diff)
    if inplace:
        write_env_file(env_file, reordered)
        click.echo(f"Written to {env_file}")

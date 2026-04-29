"""CLI commands for sorting and reordering .env file keys."""

import click

from envoy.env_file import read_env_file, write_env_file
from envoy.sort import (
    sort_keys,
    sort_by_value,
    group_and_sort,
    move_key,
    custom_order,
    format_sort_summary,
)


@click.group("sort")
def sort_cli():
    """Sort and reorder keys in .env files."""


@sort_cli.command("keys")
@click.argument("file", type=click.Path(exists=True))
@click.option("--reverse", is_flag=True, help="Sort in descending order.")
@click.option("--inplace", is_flag=True, help="Write changes back to the file.")
@click.option("--output", "-o", default=None, help="Write result to this file.")
def sort_keys_cmd(file, reverse, inplace, output):
    """Sort keys alphabetically."""
    env = read_env_file(file)
    sorted_env = sort_keys(env, reverse=reverse)
    summary = format_sort_summary(env, sorted_env)
    click.echo(summary)
    dest = file if inplace else output
    if dest:
        write_env_file(dest, sorted_env)
        click.echo(f"Written to {dest}")


@sort_cli.command("by-value")
@click.argument("file", type=click.Path(exists=True))
@click.option("--reverse", is_flag=True, help="Sort in descending order.")
@click.option("--inplace", is_flag=True, help="Write changes back to the file.")
@click.option("--output", "-o", default=None, help="Write result to this file.")
def sort_by_value_cmd(file, reverse, inplace, output):
    """Sort keys by their values."""
    env = read_env_file(file)
    sorted_env = sort_by_value(env, reverse=reverse)
    summary = format_sort_summary(env, sorted_env)
    click.echo(summary)
    dest = file if inplace else output
    if dest:
        write_env_file(dest, sorted_env)
        click.echo(f"Written to {dest}")


@sort_cli.command("group")
@click.argument("file", type=click.Path(exists=True))
@click.option("--separator", default="_", show_default=True, help="Prefix separator.")
@click.option("--inplace", is_flag=True, help="Write changes back to the file.")
@click.option("--output", "-o", default=None, help="Write result to this file.")
def group_cmd(file, separator, inplace, output):
    """Sort keys grouped by prefix."""
    env = read_env_file(file)
    sorted_env = group_and_sort(env, separator=separator)
    summary = format_sort_summary(env, sorted_env)
    click.echo(summary)
    dest = file if inplace else output
    if dest:
        write_env_file(dest, sorted_env)
        click.echo(f"Written to {dest}")


@sort_cli.command("move")
@click.argument("file", type=click.Path(exists=True))
@click.argument("key")
@click.argument("position", type=int)
@click.option("--inplace", is_flag=True, help="Write changes back to the file.")
@click.option("--output", "-o", default=None, help="Write result to this file.")
def move_cmd(file, key, position, inplace, output):
    """Move a specific key to a given index position."""
    env = read_env_file(file)
    try:
        new_env = move_key(env, key, position)
    except KeyError as e:
        raise click.ClickException(str(e))
    summary = format_sort_summary(env, new_env)
    click.echo(summary)
    dest = file if inplace else output
    if dest:
        write_env_file(dest, new_env)
        click.echo(f"Written to {dest}")

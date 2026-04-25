"""CLI commands for transforming .env file keys and values."""

import click
from envoy.env_file import read_env_file, write_env_file
from envoy.transform import (
    uppercase_keys,
    lowercase_values,
    strip_values,
    add_prefix,
    remove_prefix,
    format_transform_summary,
)


@click.group(name="transform")
def transform_cli():
    """Transform keys and values in .env files."""


@transform_cli.command("uppercase-keys")
@click.argument("file", type=click.Path(exists=True))
@click.option("--inplace", is_flag=True, help="Overwrite the source file.")
@click.option("--output", default=None, help="Write result to this file.")
def uppercase_keys_cmd(file, inplace, output):
    """Uppercase all keys in FILE."""
    env = read_env_file(file)
    result = uppercase_keys(env)
    _write_or_print(file, env, result, inplace, output)


@transform_cli.command("lowercase-values")
@click.argument("file", type=click.Path(exists=True))
@click.option("--inplace", is_flag=True)
@click.option("--output", default=None)
def lowercase_values_cmd(file, inplace, output):
    """Lowercase all values in FILE."""
    env = read_env_file(file)
    result = lowercase_values(env)
    _write_or_print(file, env, result, inplace, output)


@transform_cli.command("strip")
@click.argument("file", type=click.Path(exists=True))
@click.option("--inplace", is_flag=True)
@click.option("--output", default=None)
def strip_cmd(file, inplace, output):
    """Strip surrounding whitespace from all values in FILE."""
    env = read_env_file(file)
    result = strip_values(env)
    _write_or_print(file, env, result, inplace, output)


@transform_cli.command("add-prefix")
@click.argument("file", type=click.Path(exists=True))
@click.argument("prefix")
@click.option("--inplace", is_flag=True)
@click.option("--output", default=None)
def add_prefix_cmd(file, prefix, inplace, output):
    """Add PREFIX to all keys in FILE."""
    env = read_env_file(file)
    result = add_prefix(env, prefix)
    _write_or_print(file, env, result, inplace, output)


@transform_cli.command("remove-prefix")
@click.argument("file", type=click.Path(exists=True))
@click.argument("prefix")
@click.option("--inplace", is_flag=True)
@click.option("--output", default=None)
def remove_prefix_cmd(file, prefix, inplace, output):
    """Remove PREFIX from matching keys in FILE."""
    env = read_env_file(file)
    result = remove_prefix(env, prefix)
    _write_or_print(file, env, result, inplace, output)


def _write_or_print(source, original, transformed, inplace, output):
    summary = format_transform_summary(original, transformed)
    if summary:
        click.echo("Changes:")
        for line in summary:
            click.echo(line)
    else:
        click.echo("No changes.")

    dest = source if inplace else output
    if dest:
        write_env_file(dest, transformed)
        click.echo(f"Written to {dest}")

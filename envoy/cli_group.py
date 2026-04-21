"""CLI commands for grouping and organizing .env keys by prefix or label."""

import click
from envoy.group import group_by_prefix, group_by_labels, list_groups, format_groups, get_group
from envoy.env_file import read_env_file
from envoy.tags import load_tags


@click.group(name="group")
def group_cli():
    """Group and organize environment variables by prefix or label."""
    pass


@group_cli.command(name="by-prefix")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--separator", "-s", default="_", show_default=True, help="Separator character for prefix splitting.")
@click.option("--group", "-g", "filter_group", default=None, help="Show only a specific group.")
def by_prefix_cmd(env_file, separator, filter_group):
    """Group keys in ENV_FILE by their prefix.

    Keys are split on the separator (default: '_') and grouped by the first segment.
    Keys without the separator are placed in 'ungrouped'.
    """
    env = read_env_file(env_file)
    groups = group_by_prefix(env, separator=separator)

    if filter_group:
        result = get_group(groups, filter_group)
        if result is None:
            click.echo(f"Group '{filter_group}' not found.", err=True)
            raise SystemExit(1)
        groups = {filter_group: result}

    if not groups:
        click.echo("No groups found.")
        return

    click.echo(format_groups(groups))


@group_cli.command(name="by-label")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--profile", "-p", default=None, help="Profile name to load tags from (uses file path if omitted).")
@click.option("--group", "-g", "filter_group", default=None, help="Show only a specific label group.")
def by_label_cmd(env_file, profile, filter_group):
    """Group keys in ENV_FILE by their assigned tags/labels.

    Tags are loaded from the profile tag store. Keys without tags appear under 'untagged'.
    """
    env = read_env_file(env_file)
    label_source = profile if profile else env_file
    tags = load_tags(label_source)

    # Build a key -> [labels] mapping from the tags store
    key_labels: dict[str, list[str]] = {}
    for tag, keys in tags.items():
        for key in keys:
            key_labels.setdefault(key, []).append(tag)

    groups = group_by_labels(env, key_labels)

    if filter_group:
        result = get_group(groups, filter_group)
        if result is None:
            click.echo(f"Label group '{filter_group}' not found.", err=True)
            raise SystemExit(1)
        groups = {filter_group: result}

    if not groups:
        click.echo("No label groups found.")
        return

    click.echo(format_groups(groups))


@group_cli.command(name="list")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--separator", "-s", default="_", show_default=True, help="Separator character for prefix splitting.")
def list_cmd(env_file, separator):
    """List available prefix groups in ENV_FILE without showing their keys."""
    env = read_env_file(env_file)
    groups = group_by_prefix(env, separator=separator)
    names = list_groups(groups)

    if not names:
        click.echo("No groups found.")
        return

    for name in sorted(names):
        count = len(groups[name])
        click.echo(f"  {name} ({count} key{'s' if count != 1 else ''})")

"""CLI commands for merging .env files."""

import click
from envoy.env_file import read_env_file, write_env_file
from envoy.merge import merge_envs, merge_summary, STRATEGY_OURS, STRATEGY_THEIRS, STRATEGY_PROMPT


@click.group()
def merge_cli():
    """Merge .env files."""
    pass


@merge_cli.command("files")
@click.argument("base_file", type=click.Path(exists=True))
@click.argument("other_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file (default: overwrite base)")
@click.option(
    "--strategy",
    type=click.Choice([STRATEGY_OURS, STRATEGY_THEIRS, STRATEGY_PROMPT]),
    default=STRATEGY_OURS,
    show_default=True,
    help="Conflict resolution strategy.",
)
def merge_files(base_file, other_file, output, strategy):
    """Merge OTHER_FILE into BASE_FILE."""
    base = read_env_file(base_file)
    other = read_env_file(other_file)

    merged = merge_envs(base, other, strategy=strategy)
    summary = merge_summary(base, other, merged)

    dest = output or base_file
    write_env_file(dest, merged)

    click.echo(f"Merged into: {dest}")
    if summary["added"]:
        click.echo(f"  Added:      {', '.join(summary['added'])}")
    if summary["overridden"]:
        click.echo(f"  Overridden: {', '.join(summary['overridden'])}")
    if summary["kept"]:
        click.echo(f"  Kept ours:  {', '.join(summary['kept'])}")
    if not any(summary.values()):
        click.echo("  No changes.")

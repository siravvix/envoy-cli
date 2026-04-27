"""CLI commands for promoting env variables between profiles."""

import click
from envoy.promote import promote_keys, promote_summary, promote_profile, PromoteError
from envoy.env_file import read_env_file, write_env_file


@click.group(name="promote")
def promote_cli():
    """Promote environment variables from one profile or file to another."""


@promote_cli.command(name="files")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--key", "-k", multiple=True, help="Specific keys to promote (default: all).")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in target.")
@click.option("--dry-run", is_flag=True, default=False, help="Show changes without writing.")
def promote_files(source, target, key, overwrite, dry_run):
    """Promote keys from SOURCE .env file into TARGET .env file."""
    src_env = read_env_file(source)
    tgt_env = read_env_file(target)
    keys = list(key) if key else None
    try:
        result = promote_keys(src_env, tgt_env, keys=keys, overwrite=overwrite)
    except PromoteError as e:
        raise click.ClickException(str(e))

    summary = promote_summary(src_env, tgt_env, result)
    for k in summary["added"]:
        click.echo(click.style(f"+ {k}={result[k]}", fg="green"))
    for k in summary["updated"]:
        click.echo(click.style(f"~ {k}={result[k]}", fg="yellow"))
    for k in summary["unchanged"]:
        click.echo(f"  {k} (unchanged)")

    if not dry_run:
        write_env_file(target, result)
        click.echo(f"\nPromoted to '{target}' ({len(summary['added'])} added, {len(summary['updated'])} updated).")
    else:
        click.echo("\n[dry-run] No changes written.")


@promote_cli.command(name="profile")
@click.argument("source_profile")
@click.argument("target_profile")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--key", "-k", multiple=True, help="Specific keys to promote.")
@click.option("--overwrite", is_flag=True, default=False)
def promote_profile_cmd(source_profile, target_profile, password, key, overwrite):
    """Promote keys from SOURCE_PROFILE into TARGET_PROFILE."""
    keys = list(key) if key else None
    try:
        summary = promote_profile(
            source_profile, target_profile, password, keys=keys, overwrite=overwrite
        )
    except PromoteError as e:
        raise click.ClickException(str(e))

    click.echo(f"Added:     {', '.join(summary['added']) or 'none'}")
    click.echo(f"Updated:   {', '.join(summary['updated']) or 'none'}")
    click.echo(f"Unchanged: {len(summary['unchanged'])} key(s)")
    click.echo(click.style("Promotion complete.", fg="green"))

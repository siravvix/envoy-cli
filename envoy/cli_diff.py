"""CLI commands for diffing .env files and profiles."""
import click
from envoy.env_file import read_env_file, parse_env
from envoy.profiles import load_profile
from envoy.diff import diff_envs, format_diff


@click.group()
def diff_cli():
    """Diff commands for comparing .env files."""
    pass


@diff_cli.command("files")
@click.argument("base_file", type=click.Path(exists=True))
@click.argument("other_file", type=click.Path(exists=True))
def diff_files(base_file, other_file):
    """Compare two .env files and show differences."""
    base_raw = read_env_file(base_file)
    other_raw = read_env_file(other_file)
    base = parse_env(base_raw)
    other = parse_env(other_raw)
    result = diff_envs(base, other)
    click.echo(format_diff(result))


@diff_cli.command("profiles")
@click.argument("base_profile")
@click.argument("other_profile")
@click.option("--password", prompt=True, hide_input=True, help="Decryption password.")
def diff_profiles(base_profile, other_profile, password):
    """Compare two saved profiles and show differences."""
    try:
        base = load_profile(base_profile, password)
        other = load_profile(other_profile, password)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    result = diff_envs(base, other)
    click.echo(format_diff(result))

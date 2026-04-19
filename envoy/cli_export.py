"""CLI commands for exporting .env files to various formats."""
import sys
import click
from envoy.env_file import read_env_file, parse_env
from envoy.export import export_env, FORMATS


@click.group(name="export")
def export_cli():
    """Export .env files to other formats."""


@export_cli.command(name="convert")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format", "-f", "fmt",
    type=click.Choice(list(FORMATS.keys())),
    default="shell",
    show_default=True,
    help="Output format.",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Write to file instead of stdout.")
@click.option("--password", "-p", default=None, help="Password if file is encrypted.")
def convert(env_file, fmt, output, password):
    """Convert ENV_FILE to the specified format."""
    try:
        raw = read_env_file(env_file, password=password)
        env = parse_env(raw)
        result = export_env(env, fmt)
        if output:
            with open(output, "w") as f:
                f.write(result + "\n")
            click.echo(f"Exported to {output}")
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@export_cli.command(name="formats")
def list_formats():
    """List available export formats."""
    for fmt in FORMATS:
        click.echo(fmt)

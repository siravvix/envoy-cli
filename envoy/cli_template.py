"""CLI commands for .env template rendering."""
import click
from envoy.template import render_template_file, missing_variables, parse_template
from envoy.env_file import read_env_file


@click.group(name="template")
def template_cli():
    """Generate .env files from templates."""


@template_cli.command("render")
@click.argument("template_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("-e", "--env-file", "env_file", type=click.Path(exists=True), default=None,
              help=".env file to source values from.")
@click.option("-v", "--var", "vars_", multiple=True, metavar="KEY=VALUE",
              help="Inline variable overrides (KEY=VALUE).")
@click.option("--strict", is_flag=True, default=False,
              help="Fail if any template variable is missing.")
def render(template_file, output_file, env_file, vars_, strict):
    """Render TEMPLATE_FILE into OUTPUT_FILE using values from an env file and/or inline vars."""
    values = {}
    if env_file:
        values.update(read_env_file(env_file))
    for item in vars_:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item}")
        k, v = item.split("=", 1)
        values[k.strip()] = v.strip()
    try:
        render_template_file(template_file, output_file, values, strict=strict)
        click.echo(f"Rendered template to {output_file}")
    except KeyError as e:
        raise click.ClickException(str(e))


@template_cli.command("check")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("-e", "--env-file", "env_file", type=click.Path(exists=True), default=None)
def check(template_file, env_file):
    """Check a template for missing variables against an env file."""
    values = {}
    if env_file:
        values.update(read_env_file(env_file))
    with open(template_file) as f:
        template_str = f.read()
    missing = missing_variables(template_str, values)
    if missing:
        click.echo("Missing variables (no default):")
        for v in missing:
            click.echo(f"  - {v}")
        raise SystemExit(1)
    else:
        click.echo("All template variables are satisfied.")

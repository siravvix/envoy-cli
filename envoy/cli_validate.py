"""CLI commands for validating .env files against a schema."""
import click
import json
from envoy.env_file import read_env_file, parse_env
from envoy.validate import validate_env, format_violations, load_schema


@click.group(name="validate")
def validate_cli():
    """Validate .env files against a schema."""
    pass


@validate_cli.command()
@click.argument("env_file")
@click.argument("schema_file")
@click.option("--strict", is_flag=True, help="Exit with error code if violations found.")
def check(env_file, schema_file, strict):
    """Check ENV_FILE against SCHEMA_FILE (JSON schema)."""
    try:
        raw = read_env_file(env_file)
        env = parse_env(raw)
    except Exception as e:
        click.echo(f"Error reading env file: {e}", err=True)
        raise SystemExit(1)

    try:
        schema = load_schema(schema_file)
    except Exception as e:
        click.echo(f"Error reading schema file: {e}", err=True)
        raise SystemExit(1)

    violations = validate_env(env, schema)
    if violations:
        click.echo(f"Found {len(violations)} violation(s):")
        click.echo(format_violations(violations))
        if strict:
            raise SystemExit(1)
    else:
        click.echo("All checks passed.")


@validate_cli.command(name="show-schema")
@click.argument("schema_file")
def show_schema(schema_file):
    """Pretty-print a schema file."""
    try:
        schema = load_schema(schema_file)
        click.echo(json.dumps(schema, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

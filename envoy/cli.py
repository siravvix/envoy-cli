import click
from pathlib import Path
from envoy.env_file import read_env_file, write_env_file, encrypt_env_file, decrypt_env_file


@click.group()
def cli():
    """envoy-cli: manage and sync .env files with encryption support."""
    pass


@cli.command()
@click.argument("env_file", default=".env", type=click.Path())
@click.option("--password", prompt=True, hide_input=True, help="Encryption password")
@click.option("--output", "-o", default=None, help="Output file path (default: <env_file>.enc)")
def encrypt(env_file, password, output):
    """Encrypt an .env file."""
    input_path = Path(env_file)
    if not input_path.exists():
        raise click.ClickException(f"File not found: {env_file}")
    output_path = output or str(input_path) + ".enc"
    encrypt_env_file(str(input_path), output_path, password)
    click.echo(f"Encrypted '{env_file}' -> '{output_path}'")


@cli.command()
@click.argument("enc_file", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="Decryption password")
@click.option("--output", "-o", default=None, help="Output file path (default: .env)")
def decrypt(enc_file, password, output):
    """Decrypt an encrypted .env file."""
    output_path = output or ".env"
    output_path_obj = Path(output_path)
    if output_path_obj.exists():
        click.confirm(f"'{output_path}' already exists. Overwrite?", abort=True)
    try:
        decrypt_env_file(enc_file, output_path, password)
        click.echo(f"Decrypted '{enc_file}' -> '{output_path}'")
    except Exception:
        raise click.ClickException("Decryption failed. Wrong password or corrupted file.")


@cli.command()
@click.argument("env_file", default=".env", type=click.Path(exists=True))
def show(env_file):
    """Display key names from an .env file (values hidden)."""
    data = read_env_file(env_file)
    if not data:
        click.echo("No variables found.")
        return
    click.echo(f"Variables in '{env_file}':")
    for key in data:
        click.echo(f"  {key}=***")


@cli.command()
@click.argument("env_file", default=".env", type=click.Path(exists=True))
@click.argument("key")
def get(env_file, key):
    """Get the value of a specific key from an .env file."""
    data = read_env_file(env_file)
    if key not in data:
        raise click.ClickException(f"Key '{key}' not found in '{env_file}'")
    click.echo(data[key])


if __name__ == "__main__":
    cli()

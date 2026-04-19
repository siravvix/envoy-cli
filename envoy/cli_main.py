"""Main CLI entry point aggregating all sub-commands."""
import click
from envoy.cli import cli as core_cli
from envoy.cli_diff import diff_cli
from envoy.cli_merge import merge_cli
from envoy.cli_template import template_cli
from envoy.cli_rotate import rotate_cli
from envoy.cli_lint import lint_cli
from envoy.cli_export import export_cli
from envoy.cli_history import history_cli
from envoy.cli_import_export import transfer_cli


@click.group()
def main():
    """envoy-cli — manage and sync .env files with encryption."""
    pass


main.add_command(core_cli, name="env")
main.add_command(diff_cli, name="diff")
main.add_command(merge_cli, name="merge")
main.add_command(template_cli, name="template")
main.add_command(rotate_cli, name="rotate")
main.add_command(lint_cli, name="lint")
main.add_command(export_cli, name="export")
main.add_command(history_cli, name="history")
main.add_command(transfer_cli, name="transfer")


if __name__ == "__main__":
    main()

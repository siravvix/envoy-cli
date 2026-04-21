"""Main CLI entry point for envoy."""

import click
from envoy.cli import cli
from envoy.cli_diff import diff_cli
from envoy.cli_merge import merge_cli
from envoy.cli_template import template_cli
from envoy.cli_rotate import rotate_cli
from envoy.cli_lint import lint_cli
from envoy.cli_export import export_cli
from envoy.cli_history import history_cli
from envoy.cli_import_export import transfer_cli
from envoy.cli_search import search_cli
from envoy.cli_validate import validate_cli
from envoy.cli_completion import completion_cli
from envoy.cli_tags import tags_cli
from envoy.cli_pin import pin_cli
from envoy.cli_rename import rename_cli


@click.group()
def main():
    """envoy — manage and sync .env files with encryption support."""


main.add_command(cli)
main.add_command(diff_cli)
main.add_command(merge_cli)
main.add_command(template_cli)
main.add_command(rotate_cli)
main.add_command(lint_cli)
main.add_command(export_cli)
main.add_command(history_cli)
main.add_command(transfer_cli)
main.add_command(search_cli)
main.add_command(validate_cli)
main.add_command(completion_cli)
main.add_command(tags_cli)
main.add_command(pin_cli)
main.add_command(rename_cli)


if __name__ == "__main__":
    main()

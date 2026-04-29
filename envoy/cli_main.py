"""Main CLI entry point for envoy — aggregates all sub-command groups."""

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
from envoy.cli_search import search_cli
from envoy.cli_validate import validate_cli
from envoy.cli_completion import completion_cli
from envoy.cli_tags import tags_cli
from envoy.cli_pin import pin_cli
from envoy.cli_rename import rename_cli
from envoy.cli_group import group_cli
from envoy.cli_backup import backup_cli
from envoy.cli_alias import alias_cli
from envoy.cli_scope import scope_cli
from envoy.cli_transform import transform_cli
from envoy.cli_interpolate import interpolate_cli
from envoy.cli_chain import chain_cli
from envoy.cli_mask import mask_cli
from envoy.cli_promote import promote_cli
from envoy.cli_freeze import freeze_cli
from envoy.cli_resolve import resolve_cli


@click.group()
@click.version_option(prog_name="envoy")
def main():
    """envoy — manage and sync .env files across environments."""


main.add_command(core_cli, name="env")
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
main.add_command(group_cli)
main.add_command(backup_cli)
main.add_command(alias_cli)
main.add_command(scope_cli)
main.add_command(transform_cli)
main.add_command(interpolate_cli)
main.add_command(chain_cli)
main.add_command(mask_cli)
main.add_command(promote_cli)
main.add_command(freeze_cli)
main.add_command(resolve_cli)


if __name__ == "__main__":
    main()

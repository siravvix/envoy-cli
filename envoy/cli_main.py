"""Main CLI entry point that registers all sub-command groups."""

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


@click.group()
@click.version_option(package_name="envoy-cli")
def main():
    """envoy — manage and sync .env files across environments."""


_groups = [
    core_cli, diff_cli, merge_cli, template_cli, rotate_cli, lint_cli,
    export_cli, history_cli, transfer_cli, search_cli, validate_cli,
    completion_cli, tags_cli, pin_cli, rename_cli, group_cli, backup_cli,
    alias_cli, scope_cli, transform_cli, interpolate_cli, chain_cli,
    mask_cli, promote_cli,
]

for _grp in _groups:
    try:
        main.add_command(_grp)
    except Exception:
        pass


if __name__ == "__main__":
    main()

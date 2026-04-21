"""Shell completion helpers for envoy-cli."""

import os
from typing import List, Optional

from envoy.env_file import read_env_file, parse_env
from envoy.profiles import list_profiles


def get_env_keys(filepath: str) -> List[str]:
    """Return all keys from a .env file for shell completion."""
    try:
        raw = read_env_file(filepath)
        env = parse_env(raw)
        return list(env.keys())
    except Exception:
        return []


def get_profile_names() -> List[str]:
    """Return all saved profile names for shell completion."""
    try:
        return list_profiles()
    except Exception:
        return []


def generate_bash_completion(script_name: str = "envoy") -> str:
    """Generate a bash completion script for the CLI."""
    return f"""# Bash completion for {script_name}
_{script_name.upper()}_COMPLETION() {{
    local cur prev
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"

    local commands="encrypt decrypt show get diff merge lint export import rotate validate search history"

    case "$prev" in
        {script_name})
            COMPREPLY=($(compgen -W "$commands" -- "$cur"))
            return 0
            ;;
        --profile)
            local profiles=$(envoy complete profiles 2>/dev/null)
            COMPREPLY=($(compgen -W "$profiles" -- "$cur"))
            return 0
            ;;
        --file|-f)
            COMPREPLY=($(compgen -f -X '!*.env' -- "$cur"))
            return 0
            ;;
    esac

    COMPREPLY=($(compgen -f -- "$cur"))
}}
complete -F _{script_name.upper()}_COMPLETION {script_name}
"""


def generate_zsh_completion(script_name: str = "envoy") -> str:
    """Generate a zsh completion script for the CLI."""
    return f"""#compdef {script_name}
_{script_name}() {{
    local -a commands
    commands=(
        'encrypt:Encrypt a .env file'
        'decrypt:Decrypt a .env file'
        'show:Show contents of a .env file'
        'get:Get a specific key from a .env file'
        'diff:Diff two .env files or profiles'
        'merge:Merge two .env files'
        'lint:Lint a .env file'
        'export:Export .env to another format'
        'rotate:Rotate encryption key'
        'validate:Validate against a schema'
        'search:Search keys or values'
        'history:Manage file history'
        'complete:Output shell completion script'
    )
    _describe 'command' commands
}}
_{script_name}
"""

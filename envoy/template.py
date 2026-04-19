"""Template support: generate .env files from a template with variable substitution."""
import re
from typing import Dict, Optional

TEMPLATE_VAR_RE = re.compile(r"\{\{\s*(\w+)\s*(?::-([^}]*))?\s*\}\}")


def parse_template(template_str: str) -> list:
    """Return list of (var_name, default_value) tuples found in template."""
    return [
        (m.group(1), m.group(2))
        for m in TEMPLATE_VAR_RE.finditer(template_str)
    ]


def render_template(template_str: str, values: Dict[str, str], strict: bool = False) -> str:
    """Render a template string substituting {{ VAR }} or {{ VAR:-default }}.

    Args:
        template_str: Raw template content.
        values: Mapping of variable names to values.
        strict: If True, raise KeyError for missing vars with no default.

    Returns:
        Rendered string.
    """
    def replace(match):
        var = match.group(1)
        default = match.group(2)
        if var in values:
            return values[var]
        if default is not None:
            return default
        if strict:
            raise KeyError(f"Missing required template variable: {var}")
        return match.group(0)

    return TEMPLATE_VAR_RE.sub(replace, template_str)


def render_template_file(
    template_path: str,
    output_path: str,
    values: Dict[str, str],
    strict: bool = False,
) -> None:
    """Read a template file, render it, and write the output."""
    with open(template_path, "r") as f:
        template_str = f.read()
    rendered = render_template(template_str, values, strict=strict)
    with open(output_path, "w") as f:
        f.write(rendered)


def missing_variables(template_str: str, values: Dict[str, str]) -> list:
    """Return list of variable names that are missing (no value and no default)."""
    missing = []
    for var, default in parse_template(template_str):
        if var not in values and default is None:
            missing.append(var)
    return missing

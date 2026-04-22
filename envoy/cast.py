"""Type casting utilities for .env values."""

from typing import Any, Dict, Optional

SUPPORTED_TYPES = ["str", "int", "float", "bool", "list"]


class CastError(ValueError):
    pass


def cast_value(value: str, to_type: str) -> Any:
    """Cast a string value to the specified type."""
    if to_type == "str":
        return value
    elif to_type == "int":
        try:
            return int(value)
        except ValueError:
            raise CastError(f"Cannot cast {value!r} to int")
    elif to_type == "float":
        try:
            return float(value)
        except ValueError:
            raise CastError(f"Cannot cast {value!r} to float")
    elif to_type == "bool":
        if value.lower() in ("true", "1", "yes", "on"):
            return True
        elif value.lower() in ("false", "0", "no", "off"):
            return False
        else:
            raise CastError(f"Cannot cast {value!r} to bool")
    elif to_type == "list":
        return [item.strip() for item in value.split(",") if item.strip()]
    else:
        raise CastError(f"Unsupported type: {to_type!r}. Choose from {SUPPORTED_TYPES}")


def cast_env(env: Dict[str, str], schema: Dict[str, str]) -> Dict[str, Any]:
    """Cast multiple env values according to a type schema.

    Args:
        env: Raw env dict of string values.
        schema: Mapping of key -> type string.

    Returns:
        Dict with values cast to their declared types.
    """
    result: Dict[str, Any] = dict(env)
    errors: Dict[str, str] = {}

    for key, to_type in schema.items():
        if key not in env:
            continue
        try:
            result[key] = cast_value(env[key], to_type)
        except CastError as exc:
            errors[key] = str(exc)

    if errors:
        msg = "; ".join(f"{k}: {v}" for k, v in errors.items())
        raise CastError(f"Cast errors: {msg}")

    return result


def format_cast_result(result: Dict[str, Any]) -> str:
    """Format a cast result dict for display."""
    lines = []
    for key, value in result.items():
        type_name = type(value).__name__
        lines.append(f"{key}={value!r}  ({type_name})")
    return "\n".join(lines)

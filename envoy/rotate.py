"""Key rotation: re-encrypt env files with a new password."""

from envoy.env_file import read_env_file, write_env_file, encrypt_env_file, decrypt_env_file
from envoy.audit import log_event


def rotate_key(filepath: str, old_password: str, new_password: str) -> dict:
    """
    Re-encrypt an env file with a new password.
    Returns a summary dict with 'status' and 'keys_rotated'.

    Raises:
        ValueError: If old_password and new_password are identical.
        FileNotFoundError: If the file does not exist.
        DecryptionError: If the old password is incorrect.
    """
    if old_password == new_password:
        raise ValueError("New password must differ from the old password.")

    env = decrypt_env_file(filepath, old_password)
    encrypt_env_file(filepath, env, new_password)
    log_event(
        "rotate",
        profile=None,
        extra={"file": filepath, "keys_rotated": len(env)},
    )
    return {"status": "ok", "keys_rotated": len(env)}


def rotate_profile_key(
    profile_name: str, old_password: str, new_password: str
) -> dict:
    """
    Re-encrypt a named profile stored in the default profiles directory.

    Raises:
        ValueError: If old_password and new_password are identical.
        FileNotFoundError: If the profile does not exist.
    """
    from envoy.profiles import get_profiles_dir
    import os

    profile_path = os.path.join(get_profiles_dir(), f"{profile_name}.env.enc")
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile '{profile_name}' not found at {profile_path}")

    result = rotate_key(profile_path, old_password, new_password)
    result["profile"] = profile_name
    log_event("rotate_profile", profile=profile_name, extra={"keys_rotated": result["keys_rotated"]})
    return result

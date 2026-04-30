"""Encryption and decryption utilities for .env file contents."""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.exceptions import InvalidTag


SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a password using Scrypt."""
    kdf = Scrypt(salt=salt, length=KEY_SIZE, n=2**14, r=8, p=1)
    return kdf.derive(password.encode())


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt plaintext string and return a base64-encoded ciphertext."""
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    payload = salt + nonce + ciphertext
    return base64.b64encode(payload).decode()


def decrypt(encoded: str, password: str) -> str:
    """Decrypt a base64-encoded ciphertext string and return plaintext.

    Raises:
        ValueError: If the payload is too short to contain salt and nonce,
            or if the password is incorrect / data is corrupted.
    """
    payload = base64.b64decode(encoded.encode())
    min_size = SALT_SIZE + NONCE_SIZE
    if len(payload) <= min_size:
        raise ValueError("Encrypted payload is too short or corrupted.")
    salt = payload[:SALT_SIZE]
    nonce = payload[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = payload[SALT_SIZE + NONCE_SIZE:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
    except InvalidTag:
        raise ValueError("Decryption failed: incorrect password or corrupted data.")

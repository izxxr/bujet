# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Any
from cryptography.fernet import Fernet

import secrets

__all__ = (
    "Any",
    "fernet_encrypt",
    "fernet_decrypt",
    "generate_user_token",
)

MISSING: Any = object()

def fernet_encrypt(value: str | bytes):
    """Encrypts the given value with Fernet encryption."""
    from core.config import ENCRYPTION_KEY  # circular import

    if isinstance(value, str):
        value = value.encode()

    return Fernet(ENCRYPTION_KEY).encrypt(value)


def fernet_decrypt(value: bytes) -> str:
    """Decrypts the Fernet-encrypted value."""
    from core.config import ENCRYPTION_KEY  # circular import

    return Fernet(ENCRYPTION_KEY).decrypt(value).decode()

def generate_user_token():
    """Generates a unique authorization token."""
    return secrets.token_urlsafe(36)

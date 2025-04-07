# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Any
from core import config

__all__ = (
    "make_headers",
)

def make_headers(user_id: str | None = None, user_token: str | None = None) -> dict[str, Any]:
    if not user_id:
        user_id = config.TEST_USER_ID
    if not user_token:
        user_token = config.TEST_USER_TOKEN

    if user_id is None:
        raise ValueError("No user ID available for testing")
    if user_token is None:
        raise ValueError("No user token available for testing")

    return {
        "X-User-Id": user_id,
        "X-User-Token": user_token,
    }

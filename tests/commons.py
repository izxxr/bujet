# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from core.schemas import User

__all__ = (
    "make_headers",
)

def make_headers(user: dict[str, Any] | User) -> dict[str, Any]:
    if isinstance(user, dict):
        user_id = user["id"]
        user_token = user["token"]
    else:
        user_id = user.id
        user_token = user.token

    return {
        "X-User-Id": str(user_id),
        "X-User-Token": user_token,
    }


class RouterTestState:
    """State passed to routers test."""

    __slots__ = (
        "client",
        "user",
        "baton",
    )

    def __init__(self, client: TestClient, user: User | None = None) -> None:
        self.client = client
        self.user = user
        self.baton: dict[str, Any] = {}

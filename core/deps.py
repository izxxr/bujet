# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Annotated
from fastapi import Header, Request, HTTPException
from core.utils import fernet_decrypt

__all__ = (
    "require_auth",
)


async def require_auth(request: Request, x_user_id: Annotated[str, Header()], x_user_token: Annotated[str, Header()]):
    """FastAPI dependency to validate request authorization.

    This ensures that the request has X-User-Token and X-User-Id header
    with valid authorizatoin token and user ID respectively.

    If validated, the corresponding user object is attached with request
    state in the "user" attribute.
    """
    try:
        user = await request.app.state.db.retrieve_user(x_user_id)
    except ValueError:
        raise HTTPException(404, "User not found") from None
    else:
        if fernet_decrypt(user.token) != x_user_token:
            raise HTTPException(401, "Invalid authorization token")

        request.state.user = user

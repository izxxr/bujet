# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Any, Annotated
from fastapi import APIRouter, HTTPException, Request, Response, Header, Depends
from core.deps import require_auth
from core import schemas, models, utils

__all__ = (
    "user",
)

user = APIRouter(prefix="/user")


@user.post("/")
async def create_user(data: schemas.CreateUserJSON) -> dict[str, Any]:
    """Create a user.

    This endpoint acts as the "sign up" route.

    Errors:

    - 409 Conflict: The username is already taken.
    """
    existing = await models.User.filter(username=data.username).first()
    if existing:
        raise HTTPException(409, "This username is already taken.")

    user = data.to_db_model()
    await user.save()

    # This endpoint returns a "partial" user object containing only
    # the listed fields. While it's possible to return a complete user
    # object using from_db_model(), it isn't really worth the extra processing
    # step as client most likely does not need that much information.
    return {
        "id": str(user.id),
        "username": user.username,
        "display_name": user.display_name,
        "password": data.password,
        "token": utils.fernet_decrypt(user.token),
    }

@user.get("/")
async def get_user(header: Annotated[schemas.GetUserHeader, Header()]) -> schemas.User:
    """Gets information about the user.

    This endpoint acts as the "sign in" route as it takes the
    client facing credentials (username and password) and returns
    the user information including authorization token which is
    expected to be used in subsequent requests.
    """
    user = await models.User.filter(username=header.x_user_username).first()

    if user is None or utils.fernet_decrypt(user.password) != header.x_user_password:
        raise HTTPException(404, "Invalid username or password")

    return schemas.User.from_db_model(user)

@user.patch("/", dependencies=[Depends(require_auth)])
async def update_user(request: Request, data: schemas.EditUserJSON) -> schemas.User:
    """Updates a user information.

    Returns the updated user on successful update.

    Errors:

    - 409 Conflict: The new username is already taken.
    """
    user: models.User = request.state.user
    update_data = data.to_dict()

    # Validate uniqueness of username
    if "username" in update_data:
        existing = await models.User.filter(username=update_data["username"]).first()
        if existing:
            raise HTTPException(409, "The new username is already taken.")

    user.update_from_dict(update_data)  # type: ignore
    await user.save()

    return schemas.User.from_db_model(user)

@user.delete("/", dependencies=[Depends(require_auth)])
async def delete_user(request: Request) -> Response:
    """Deletes the authorized user information.
    
    Returns 204 No Content on successful deletion.
    """
    user: models.User = request.state.user
    await user.delete()

    return Response(None, 204)

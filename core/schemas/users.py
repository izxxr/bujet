# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Self, Any
from pydantic import UUID4, Field
from functools import cached_property
from core.schemas.base import APIModel
from core.models import constraints, User as DBUser
from core import utils

import uuid

__all__ = (
    "User",
    "CreateUserJSON",
    "GetUserHeader",
    "EditUserJSON",
)


class User(APIModel):
    """Pydantic model corresponding to core.models.User.

    For the details of each field in this model, see the documentation
    of core.models.User object.

    Note that password and token of user in this field are not encrypted
    unlike the database model. The properties encrypted_password and
    encrypted_token encrypt and return the encrypted data for password and
    token respectively.
    
    These properties cache the value so they result same result each time but it
    is worth noting that Fernet encryption result is not the same each time so
    these values are not safe for comparison in general. Whenever comparison is
    required, the decrypted values should be used instead.
    """

    id: UUID4
    username: str = Field(
        min_length=constraints.USER_USERNAME_MIN_LENGTH,
        max_length=constraints.USER_USERNAME_MAX_LENGTH,
    )
    display_name: str | None = Field(
        min_length=constraints.USER_DISPLAY_NAME_MIN_LENGTH,
        max_length=constraints.USER_DISPLAY_NAME_MAX_LENGTH,
        default=None,
    )
    password: str = Field(min_length=constraints.USER_PASSWORD_MIN_LENGTH)
    token: str

    @cached_property
    def encrypted_password(self) -> bytes:
        return utils.fernet_encrypt(self.password)

    @cached_property
    def encrypted_token(self) -> bytes:
        return utils.fernet_encrypt(self.token)

    def to_db_model(self) -> DBUser:
        data = self.model_dump()
        data["password"] = self.encrypted_password
        data["token"] = self.encrypted_token
        return DBUser(**data)

    @classmethod
    def from_db_model(cls, db_model: DBUser) -> Self:
        return cls(
            id=db_model.id,
            username=db_model.username,
            display_name=db_model.display_name,
            password=utils.fernet_decrypt(db_model.password),
            token=utils.fernet_decrypt(db_model.token),
        )


class CreateUserJSON(APIModel):
    """Pydantic model representing JSON body for the POST /user or Create User endpoint.

    The fields in this schema are defined by the user model. Like core.schemas.User, the
    password field is not the encrypted password.
    """

    username: str = Field(
        min_length=constraints.USER_USERNAME_MIN_LENGTH,
        max_length=constraints.USER_USERNAME_MAX_LENGTH,
    )
    display_name: str | None = Field(
        min_length=constraints.USER_DISPLAY_NAME_MIN_LENGTH,
        max_length=constraints.USER_DISPLAY_NAME_MAX_LENGTH,
        default=None,
    )
    password: str = Field(min_length=constraints.USER_PASSWORD_MIN_LENGTH)

    def to_db_model(self) -> DBUser:
        data = self.model_dump()
        data["id"] = uuid.uuid4()
        data["password"] = utils.fernet_encrypt(data["password"])
        data["token"] = utils.fernet_encrypt(utils.generate_user_token())
        return DBUser(**data)


class GetUserHeader(APIModel):
    """Pydantic model representing JSON body for the GET /user or Get User endpoint.

    The fields in this schema are defined by the user model. Like core.schemas.User, the
    password field is not the encrypted password.
    """

    x_user_username: str = Field(
        min_length=constraints.USER_USERNAME_MIN_LENGTH,
        max_length=constraints.USER_USERNAME_MAX_LENGTH,
    )
    x_user_password: str = Field(min_length=constraints.USER_PASSWORD_MIN_LENGTH)


class EditUserJSON(APIModel):
    """Pydantic model representing JSON body for the PATCH /user or Edit User endpoint.

    The fields in this schema are defined by the user model. Like core.schemas.User, the
    password field is not the encrypted password.
    """
    username: str = Field(
        min_length=constraints.USER_USERNAME_MIN_LENGTH,
        max_length=constraints.USER_USERNAME_MAX_LENGTH,
        default=utils.MISSING,
    )
    display_name: str | None = Field(
        min_length=constraints.USER_DISPLAY_NAME_MIN_LENGTH,
        max_length=constraints.USER_DISPLAY_NAME_MAX_LENGTH,
        default=utils.MISSING,
    )
    password: str = Field(min_length=constraints.USER_PASSWORD_MIN_LENGTH, default=utils.MISSING)

    def to_dict(self) -> dict[str, Any]:
        """Returns the dictionary that can be uesd to update the model in database"""
        data = self.model_dump(exclude_defaults=True)

        # If password is changed, reset the authorization token as a
        # security measure.
        if "password" in data:
            data["password"] = utils.fernet_encrypt(data["password"])
            data["token"] = utils.fernet_encrypt(utils.generate_user_token())

        return data

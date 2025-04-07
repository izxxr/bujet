# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from core.models import constraints
from core import utils
from tortoise import Model, fields, validators

__all__ = (
    "User",
)


class User(Model):
    """Represents a registered user."""

    id = fields.UUIDField(primary_key=True)
    """The user's unique identifier encoded as UUID4."""

    username = fields.TextField(
        validators=[
            validators.MinLengthValidator(constraints.USER_USERNAME_MIN_LENGTH),
            validators.MaxLengthValidator(constraints.USER_USERNAME_MAX_LENGTH),
        ]
    )
    """The user's unique username."""

    display_name = fields.TextField(
        validators=[
            validators.MinLengthValidator(constraints.USER_DISPLAY_NAME_MIN_LENGTH),
            validators.MaxLengthValidator(constraints.USER_DISPLAY_NAME_MAX_LENGTH),
        ],
        null=True,
        default=None,
    )
    """The user's displayed name."""

    password = fields.BinaryField()
    """The user's login password encryped with Fernet.

    Since this field is in binary, the length has to be validated
    separately either manually or using Pydantic models in core.schemas.
    """

    token = fields.BinaryField(default=lambda: utils.fernet_encrypt(utils.generate_user_token()))
    """The user's unique authorization token.

    This is generated at server side and is required for authorizing
    the HTTP requests sent by client. In order to reset this token,
    the password has to be changed.
    """

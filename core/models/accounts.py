# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from tortoise import Model, fields, validators
from enum import IntEnum 
from core.models import constraints, User

__all__ = (
    "FinancialAccount",
    "AccountType",
)


class AccountType(IntEnum):
    """An enum representing the types of financial account."""

    CHECKING = 0
    """Simple checking account."""

    CASH = 1
    """Account for tracking in-hand cash."""

    WALLET = 2
    """Account for representing (digital) wallets."""


class FinancialAccount(Model):
    """Represents a financial account that keeps track of transactions."""

    id = fields.UUIDField(primary_key=True)
    """The account's unique identifier encoded as UUID4."""

    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", related_name="users")
    """The user that this account associated to."""

    name = fields.TextField(
        validators=[
            validators.MinLengthValidator(constraints.ACCOUNT_NAME_MIN_LENGTH),
            validators.MaxLengthValidator(constraints.ACCOUNT_NAME_MAX_LENGTH),
        ]
    )
    """The account's name."""

    description = fields.TextField(
        validators=[
            validators.MinLengthValidator(constraints.ACCOUNT_DESCRIPTION_MIN_LENGTH),
            validators.MaxLengthValidator(constraints.ACCOUNT_DESCRIPTION_MAX_LENGTH),
        ],
        null=True,
        default=None,
    )
    """The description of this account."""

    type = fields.IntEnumField(AccountType)
    """The type of account."""

    created_at = fields.DatetimeField(auto_now_add=True)
    """The time when this account was created."""

    currency_decimals = fields.IntField(default=2)
    """The number of decimals that the currency has that this account uses.

    Note: this field is currently neither used by server nor the client.
    Regardless, of the value of this field, the currency decimals should
    be taken as 2.

    This attribute is applicable for all transaction amounts associated
    to this account. For more information, see the "amount" field's documentation
    in Transaction model.
    """

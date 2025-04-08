# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from tortoise import Model, fields, validators
from core.models import constraints, FinancialAccount

__all__ = (
    "Transaction",
)


class Transaction(Model):
    """Represents a transaction against a financial account."""

    id = fields.UUIDField(primary_key=True)
    """The transaction's unique identifier encoded as UUID4."""

    account: fields.ForeignKeyRelation[FinancialAccount] = fields.ForeignKeyField(
        "models.FinancialAccount", related_name="accounts"
    )
    """The account that this transaction is performed against."""

    amount = fields.IntField()
    """The transaction amount in minor units format (currency decimals assumed 2).

    In general, we can say

    actual amount = amount / 100 
    """

    description = fields.TextField(
        validators=[
            validators.MinLengthValidator(constraints.TRANSACTION_DESCRIPTION_MIN_LENGTH),
            validators.MaxLengthValidator(constraints.TRANSACTION_DESCRIPTION_MAX_LENGTH),
        ],
        null=True,
        default=None,
    )
    """Text describing the transaction."""

    date = fields.DatetimeField(auto_now_add=True)
    """The date and time when this transaction was performed."""

# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Self, Any
from pydantic import UUID4, AwareDatetime, Field, field_validator
from core.utils import MISSING
from core.schemas.base import APIModel
from core.models import (
    constraints,
    Transaction as DBTransaction,
    FinancialAccount as DBFinancialAccount,
)

import datetime
import decimal
import uuid

__all__ = (
    "Transaction",
    "LogTransactionJSON",
    "EditTransactionJSON",
)


class Transaction(APIModel):
    """Pydantic model corresponding to core.models.Transaction.

    For the details of each field in this model, see the documentation
    of core.models.Transaction object.
    """

    id: UUID4
    account_id: UUID4
    amount: int
    description: str | None = Field(
        min_length=constraints.TRANSACTION_DESCRIPTION_MIN_LENGTH,
        max_length=constraints.TRANSACTION_DESCRIPTION_MAX_LENGTH,
        default=None,
    )
    date: AwareDatetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: decimal.Decimal) -> decimal.Decimal:
        if value == 0:
            raise ValueError("amount cannot be zero")
        return value

    def to_db_model(self, account: DBFinancialAccount) -> DBTransaction:
        data = self.model_dump()
        data["account"] = account
        return DBTransaction(**data)

    @classmethod
    def from_db_model(cls, db_model: DBTransaction, account: DBFinancialAccount) -> Self:
        return cls(
            id=db_model.id,
            account_id=account.id,
            amount=db_model.amount,
            description=db_model.description,
            date=db_model.date,
        )


class LogTransactionJSON(APIModel):
    """
    Pydantic model representing JSON body for the POST /accounts/{account_id}/transactions
    or Log Transaction endpoint.

    The fields in this schema are defined by the transaction model.
    """

    amount: int
    description: str | None = Field(
        min_length=constraints.TRANSACTION_DESCRIPTION_MIN_LENGTH,
        max_length=constraints.TRANSACTION_DESCRIPTION_MAX_LENGTH,
        default=None,
    )
    date: AwareDatetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: decimal.Decimal) -> decimal.Decimal:
        if value == 0:
            raise ValueError("amount cannot be zero")
        return value

    def to_db_model(self, account: DBFinancialAccount) -> DBTransaction:
        data = self.model_dump()
        data["id"] = uuid.uuid4()
        data["account_id"] = account.id
        return DBTransaction(**data)


class EditTransactionJSON(APIModel):
    """
    Pydantic model representing JSON body for the PATCH /accounts/{account_id}/transactions/{transaction_id}
    or Edit Transaction endpoint.

    The fields in this schema are defined by the transaction model.
    """

    amount: int = Field(default=MISSING)
    description: str | None = Field(
        min_length=constraints.TRANSACTION_DESCRIPTION_MIN_LENGTH,
        max_length=constraints.TRANSACTION_DESCRIPTION_MAX_LENGTH,
        default=MISSING,
    )
    date: AwareDatetime = Field(default=MISSING)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: decimal.Decimal) -> decimal.Decimal:
        if value == 0:
            raise ValueError("amount cannot be zero")
        return value

    def to_dict(self) -> dict[str, Any]:
        """Returns the dictionary that can be used to update the model in database"""
        return self.model_dump(exclude_defaults=True)

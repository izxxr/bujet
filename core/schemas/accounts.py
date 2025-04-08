# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Self, Any
from pydantic import UUID4, Field, AwareDatetime
from core.schemas.base import APIModel
from core.utils import MISSING
from core.models import (
    constraints,
    FinancialAccount as DBFinancialAccount,
    AccountType as AccountType,  # exported
    User,
)

import datetime
import uuid


__all__ = (
    "FinancialAccount",
    "AccountType",
    "CreateAccountJSON",
    "EditAccountJSON",
    "CalculateBalanceResponse",
)



class FinancialAccount(APIModel):
    """Pydantic model corresponding to core.models.FinancialAccount.

    For the details of each field in this model, see the documentation
    of core.models.FinancialAccount object.
    """

    id: UUID4
    user_id: UUID4
    name: str = Field(
        min_length=constraints.ACCOUNT_NAME_MIN_LENGTH,
        max_length=constraints.ACCOUNT_NAME_MAX_LENGTH,
    )
    description: str | None = Field(
        min_length=constraints.ACCOUNT_DESCRIPTION_MIN_LENGTH,
        max_length=constraints.ACCOUNT_DESCRIPTION_MAX_LENGTH,
        default=None,
    )
    type: AccountType = Field(default=AccountType.CHECKING)
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    currency_decimals: int = Field(default=2)

    def to_db_model(self) -> DBFinancialAccount:
        data = self.model_dump()
        return DBFinancialAccount(**data)

    @classmethod
    def from_db_model(cls, db_model: DBFinancialAccount, user: User) -> Self:
        return cls(
            id=db_model.id,
            user_id=user.id,
            name=db_model.name,
            description=db_model.description,
            created_at=db_model.created_at,
            type=db_model.type,
            currency_decimals=db_model.currency_decimals,
        )


class CreateAccountJSON(APIModel):
    """Pydantic model representing JSON body for the POST /accounts or Create Account endpoint.

    The fields in this schema are defined by the financial account model.
    """
    name: str = Field(
        min_length=constraints.ACCOUNT_NAME_MIN_LENGTH,
        max_length=constraints.ACCOUNT_NAME_MAX_LENGTH,
    )
    description: str | None = Field(
        min_length=constraints.ACCOUNT_DESCRIPTION_MIN_LENGTH,
        max_length=constraints.ACCOUNT_DESCRIPTION_MAX_LENGTH,
        default=None,
    )
    type: AccountType = Field(default=AccountType.CHECKING)
    currency_decimals: int = Field(default=2)

    def to_db_model(self, user: User) -> DBFinancialAccount:
        """Creates models.FinancialAccount from the given data.
        
        Parameters
        ----------
        user: :class:`models.User`
            The user that this account belongs to. 
        """
        data = self.model_dump()
        data["user"] = user
        data["id"] = uuid.uuid4()
        return DBFinancialAccount(**data)


class EditAccountJSON(APIModel):
    """Pydantic model representing JSON body for the PATCH /accounts/{account_id} or Edit Account endpoint.

    The fields in this schema are defined by the financial account model.
    """
    name: str = Field(
        min_length=constraints.ACCOUNT_NAME_MIN_LENGTH,
        max_length=constraints.ACCOUNT_NAME_MAX_LENGTH,
        default=MISSING,
    )
    description: str | None = Field(
        min_length=constraints.ACCOUNT_DESCRIPTION_MIN_LENGTH,
        max_length=constraints.ACCOUNT_DESCRIPTION_MAX_LENGTH,
        default=MISSING,
    )
    currency_decimals: int = Field(default=2)

    def to_dict(self) -> dict[str, Any]:
        """Returns the dictionary that can be uesd to update the model in database"""
        return self.model_dump(exclude_defaults=True)


class CalculateBalanceResponse(APIModel):
    """
    Pydantic model representing JSON body for the GET /accounts/{account_id}/balance
    or Calculate Balance endpoint.
    """

    balance: int
    """The balance in minor units format."""

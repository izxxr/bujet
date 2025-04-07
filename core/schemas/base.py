# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Any, Self
from pydantic import BaseModel

__all__ = (
    "APIModel",
)


class APIModel(BaseModel):
    """The base class for all objects returned by API."""

    def to_db_model(self, *args: Any, **kwargs: Any) -> Any:
        """Constructs the database model for this model.

        This operation is not possible for all API models and
        must be implemented by subclasses.
        """
        raise NotImplementedError("This model does not support this operation.")

    @classmethod
    def from_db_model(cls: type[Self], db_model: Any, *args: Any, **kwargs: Any) -> Self:
        """Constructs the API model from the given database model.

        This operation is not possible for all API models and
        must be implemented by subclasses.
        """
        raise NotImplementedError("This model does not support this operation.")

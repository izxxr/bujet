# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from core.datastructures import LRUCache
from core import models, config

import uuid

__all__ = (
    "DatabaseClient",
)


class DatabaseClient:
    """The database client.

    This class provides common database operations and acts as a bridge
    between database and cache.

    It is possible to perform database operations directly by initializing
    the Tortoise ORM models manually. This class only acts as an extra layer
    for operations that require some form of pre/post processing e.g. caching.
    """

    def __init__(self) -> None:
        self._users_cache = LRUCache[uuid.UUID, models.User](config.CACHE_MAX_USERS)

    async def retrieve_user(self, user_id: str | uuid.UUID) -> models.User:
        """Retrieves a user by its ID.

        This method will look up the user in cache. If found,
        returns the cached user otherwise fetches the user
        from database and caches it for subsequent calls.

        For invalid user_id, ValueError is raised.
        """
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(user_id)

        user = self._users_cache.get(user_id)

        if user is None:
            user = await models.User.filter(id=user_id).first()
            if user:
                self._users_cache.insert(user_id, user)
            else:
                raise ValueError("Invalid user_id provided.")

        return user

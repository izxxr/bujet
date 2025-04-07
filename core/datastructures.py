# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Generic, TypeVar
from collections import OrderedDict

__all__ = (
    "LRUCache",
)

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class LRUCache(Generic[_KT, _VT]):
    """Represents a simple LRU cache.

    The entries that are least accessed are discarded from the cache
    once the caching limit is reached.

    This class takes one parameter ``maxlen`` that defines the number
    of items in the cache before the least used item is evicted.
    """

    __slots__ = (
        "__maxlen",
        "__data",
    )
    
    def __init__(self, maxlen: int) -> None:
        self.__maxlen = maxlen
        self.__data: OrderedDict[_KT, _VT] = OrderedDict()

    def insert(self, key: _KT, value: _VT) -> None:
        """Inserts an entry in the cache."""
        if len(self.__data) >= self.__maxlen:
            self.__data.popitem(last=False)

        self.__data[key] = value
        self.__data.move_to_end(key, last=False)

    def get(self, key: _KT) -> _VT | None:
        """Gets a value from the cache by its key."""
        try:
            self.__data.move_to_end(key, last=False)
            return self.__data[key]
        except KeyError:
            return None

    def delete(self, key: _KT) -> _VT | None:
        """Deletes a value from the cache and returns it."""
        try:
            return self.__data.pop(key)
        except KeyError:
            return None

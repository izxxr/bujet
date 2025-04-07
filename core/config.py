# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from core.utils import MISSING as _missing

import typing as _t
import dotenv as _dotenv
import os as _os

_T = _t.TypeVar("_T")

@_t.overload
def __get_key(key: str) -> str:
    ...

@_t.overload
def __get_key(key: str, default: _T = ...) -> _T | str:
    ...

@_t.overload
def __get_key(key: str, default: _T = ..., *, as_int: _t.Literal[False]) -> _T | str:
    ...

@_t.overload
def __get_key(key: str, default: _T = ..., *, as_int: _t.Literal[True]) -> _T | int:
    ...

def __get_key(key: str, default: _T = _missing, *, as_int: bool = False) -> str | int | _T:
    try:
        value = _os.environ[key]
    except KeyError:
        if default is not _missing:
            return default
        raise ValueError(f"{key!r} environment variable is not set.") from None

    if as_int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Value for {key!r} must be an integer, got {value!r}.") from None

    return value

_dotenv.load_dotenv()


ENCRYPTION_KEY = __get_key("BUJET_ENCRYPTION_KEY")
"""Encryption used to decrypt and encrypt Fernet messages."""

CACHE_MAX_USERS = __get_key("BUJET_CACHE_MAX_USERS", 256, as_int=True)
"""The maximum number of users that are cached in memory at a time."""

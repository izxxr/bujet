# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Any
from app import app

import os


def _rm_if_exist(path: str):
    if os.path.exists(path):
        os.remove(path)

def pytest_sessionstart(*args: Any):
    app.state.pytest_running = True

def pytest_sessionfinish(*args: Any):
    _rm_if_exist("db-test.sqlite3")

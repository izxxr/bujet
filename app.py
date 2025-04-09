# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise, connections
from core.database import DatabaseClient

import contextlib
import routers

__all__ = (
    "app",
)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # pytest_running is injected in state by pytest_sessionstart hook in conftest
    db = "db-test.sqlite3" if getattr(app.state, "pytest_running", False) else "db.sqlite3"

    await Tortoise.init(db_url=f'sqlite://{db}', modules={'models': ['core.models']})  # type: ignore
    await Tortoise.generate_schemas()

    app.state.db = DatabaseClient()

    yield
    await connections.close_all()


app = FastAPI(version="0.1.0", lifespan=lifespan)
origins = [
    "https://bujet.onrender.com",
    "https://bujet-api.onrender.com",
    "http://localhost",
    "http://localhost:5000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

for router in routers.__include_routers__:
    app.include_router(router)

@app.get("/")
async def index():
    return {"version": app.version}

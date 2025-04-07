# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.commons import make_headers, RouterTestState
from app import app

import pytest

@pytest.fixture
def state():
    with TestClient(app) as c:
        yield RouterTestState(c)

def test_create_user(state: RouterTestState):
    response = state.client.post(
        "/user",
        json={
            "username": "foobar",
            "display_name": "Foobar Display",
            "password": "123456789",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("username") == "foobar"
    assert data.get("display_name") == "Foobar Display"
    assert data.get("password") == "123456789"

    response = state.client.post(
        "/user",
        json={
            "username": "foobar",
            "password": "123456789",
        }
    )

    assert response.status_code == 409

def test_get_user(state: RouterTestState):
    response = state.client.post(
        "/user",
        json={
            "username": "random user",
            "display_name": None,
            "password": "abcdefghijkl",
        }
    )

    assert response.status_code == 200

    user = response.json()
    response = state.client.get(
        "/user",
        headers={"X-User-Username": "random user", "X-User-Password": "abcdefghijkl"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("id") == user["id"]
    assert data.get("username") == user["username"]
    assert data.get("display_name") == user["display_name"]
    assert data.get("password") == user["password"]
    assert data.get("token") == user["token"]

def test_edit_user(state: RouterTestState):
    response = state.client.post(
        "/user",
        json={
            "username": "old username",
            "display_name": "old name",
            "password": "abcdefghijkl",
        }
    )

    assert response.status_code == 200
    user = response.json()

    # Test - Basic username update
    response = state.client.patch(
        "/user",
        headers=make_headers(user),
        json={"username": "new username"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("id") == user["id"]
    assert data.get("username") == "new username"
    assert data.get("display_name") == user["display_name"]
    assert data.get("password") == user["password"]
    assert data.get("token") == user["token"]

    user = data

    # Test - Token Regeneration
    response = state.client.patch(
        "/user",
        headers=make_headers(user),
        json={"password": "12345678"},
    )
    data = response.json()

    assert data.get("password") == "12345678"
    assert data.get("token") != user["token"]

    assert response.status_code == 200
    user = data

    # Test - unset field
    response = state.client.patch(
        "/user",
        headers=make_headers(user),
        json={"display_name": None},
    )
    data = response.json()

    assert response.status_code == 200
    assert data.get("display_name") == None

def test_delete_user(state: RouterTestState):
    response = state.client.post(
        "/user",
        json={
            "username": "delete user",
            "display_name": "old name",
            "password": "abcdefghijkl",
        }
    )

    assert response.status_code == 200
    user = response.json()

    # Test - Basic user deletion
    response = state.client.delete(
        "/user",
        headers=make_headers(user),
    )

    assert response.status_code == 204

    response = state.client.get(
        "/user",
        headers={"X-User-Username": user["username"], "X-User-Password": user["password"]},
    )

    assert response.status_code == 404

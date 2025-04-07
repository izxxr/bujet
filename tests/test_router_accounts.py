# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.commons import make_headers, RouterTestState
from core.schemas import User
from app import app

import pytest

@pytest.fixture(scope="module")
def state():
    with TestClient(app) as client:
        response = client.post(
            "/user",
            json={
                "username": "tester-router-accounts",
                "password": "123456789",
            }
        )

        assert response.status_code == 200

        yield RouterTestState(client, User(**response.json()))


def test_create_account(state: RouterTestState):
    assert state.user is not None

    response = state.client.post(
        "/accounts",
        json={
            "name": "Bank",
            "description": "My bank account",
            "type": 1,
        },
        headers=make_headers(state.user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("name") == "Bank"
    assert data.get("description") == "My bank account"
    assert data.get("type") == 1

    response = state.client.post(
        "/accounts",
        json={
            "name": "Normal",
            "description": "My checking account",
        },
        headers=make_headers(state.user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("name") == "Normal"
    assert data.get("description") == "My checking account"
    assert data.get("type") == 0

def test_get_all_accounts(state: RouterTestState):
    assert state.user is not None

    response = state.client.get(
        "/accounts",
        headers=make_headers(state.user),
    )

    assert response.status_code == 200

    accounts = response.json()

    assert len(accounts) == 2

    assert accounts[0].get("name") == "Bank"
    assert accounts[0].get("description") == "My bank account"
    assert accounts[0].get("type") == 1

    assert accounts[1].get("name") == "Normal"
    assert accounts[1].get("description") == "My checking account"
    assert accounts[1].get("type") == 0

def test_get_account(state: RouterTestState):
    assert state.user is not None

    response = state.client.post(
        "/accounts",
        json={"name": "temp account"},
        headers=make_headers(state.user),
    )

    assert response.status_code == 200
    created_account = response.json()

    response = state.client.get(
        "/accounts/{account_id}".format(account_id=created_account["id"]),
        headers=make_headers(state.user),
    )

    assert response.status_code == 200
    account = response.json()

    assert account["id"] == created_account["id"]
    assert account["name"] == created_account["name"]
    assert account["description"] == created_account["description"]
    assert account["type"] == created_account["type"]
    assert account["created_at"] == created_account["created_at"]

def test_edit_account(state: RouterTestState):
    assert state.user is not None

    response = state.client.post(
        "/accounts",
        json={"name": "old account name", "description": "account description"},
        headers=make_headers(state.user),
    )

    assert response.status_code == 200
    account = response.json()

    # Test - Basic name update
    response = state.client.patch(
        "/accounts/{account_id}".format(account_id=account["id"]),
        headers=make_headers(state.user),
        json={"name": "new account name"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data.get("id") == account["id"]
    assert data.get("name") == "new account name"
    assert data.get("description") == account["description"]
    assert data.get("type") == account["type"]
    assert data.get("created_at") == account["created_at"]

    account = data

    # Test - unset field
    response = state.client.patch(
        "/accounts/{account_id}".format(account_id=account["id"]),
        headers=make_headers(state.user),
        json={"description": None},
    )
    data = response.json()

    assert response.status_code == 200
    assert data.get("description") == None

def test_delete_user(state: RouterTestState):
    assert state.user is not None

    response = state.client.post(
        "/accounts",
        json={"name": "delete account"},
        headers=make_headers(state.user),
    )

    assert response.status_code == 200
    account = response.json()

    # Test - Basic user deletion
    response = state.client.delete(
        "/accounts/{account_id}".format(account_id=account["id"]),
        headers=make_headers(state.user),
    )

    assert response.status_code == 204

    response = state.client.get(
        "/accounts/{account_id}".format(account_id=account["id"]),
        headers=make_headers(state.user),
    )

    assert response.status_code == 404

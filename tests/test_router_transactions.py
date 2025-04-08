# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from typing import Any
from fastapi.testclient import TestClient
from tests.commons import make_headers, RouterTestState
from core.schemas import User, FinancialAccount
from app import app

import pytest
import datetime

def _date_std_isoformat(*args: Any, **kwargs: Any) -> str:
    # Python's isoformat does not include 'Z' as timezone
    # information. For proper comparison, we need to replace
    # UTC offset +00:00 with Z.
    # See https://stackoverflow.com/questions/19654578/python-utc-datetime-objects-iso-format-doesnt-include-z-zulu-or-zero-offset
    iso = datetime.datetime(*args, **kwargs).isoformat()
    return iso.replace("+00:00", "Z")

@pytest.fixture(scope="module")
def state():
    with TestClient(app) as client:
        response = client.post(
            "/user",
            json={
                "username": "tester-router-transactions",
                "password": "123456789",
            }
        )
        assert response.status_code == 200

        state = RouterTestState(client, User(**response.json()))
        assert state.user is not None

        response = state.client.post(
            "/accounts",
            json={"name": "Bank"},
            headers=make_headers(state.user),
        )
        assert response.status_code == 200
        state.baton["account"] = FinancialAccount(**response.json())

        yield state


# This test requires a clean transaction table state so it is tested first.
def test_list_transactions(state: RouterTestState):
    assert state.user is not None

    transactions: list[dict[str, Any]] = [
        {"amount": 133, "date": _date_std_isoformat(2023, 11, 9, tzinfo=datetime.timezone.utc)},
        {"amount": -12, "date": _date_std_isoformat(2024, 3, 1, tzinfo=datetime.timezone.utc)},
        {"amount": 2512, "date": _date_std_isoformat(2024, 12, 11, tzinfo=datetime.timezone.utc)},
        {"amount": 3200, "date": _date_std_isoformat(2025, 8, 4, tzinfo=datetime.timezone.utc)},
        {"amount": -532, "date": _date_std_isoformat(2025, 8, 6, tzinfo=datetime.timezone.utc)},
        {"amount": 3211, "date": _date_std_isoformat(2025, 9, 12, tzinfo=datetime.timezone.utc)},
        {"amount": 999, "date": _date_std_isoformat(2025, 12, 11, tzinfo=datetime.timezone.utc)},
    ]
    responses: list[dict[str, Any]] = []

    for transaction in transactions:
        response = state.client.post(
            "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
            json=transaction,
            headers=make_headers(state.user),
        )
        print(response.json())
        assert response.status_code == 200
        responses.append(response.json())

    transactions = responses

    # Test - get latest transactions
    response = state.client.get(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        headers=make_headers(state.user),
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == len(transactions)

    balance = 0

    for idx, recv_transaction in enumerate(data):
        assert recv_transaction == responses[idx]
        balance += responses[idx]["amount"]

    state.baton["balance"] = balance  # for the next test

    # Test - get 3 latest transactions
    response = state.client.get(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        headers=make_headers(state.user),
        params={"limit": 3}
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3

    for idx, recv_transaction in enumerate(data[:3]):
        assert recv_transaction == transactions[idx]

    # Test - Get transactions after a date
    response = state.client.get(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        headers=make_headers(state.user),
        params={"after": _date_std_isoformat(2025, 9, 12, tzinfo=datetime.timezone.utc)}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    assert data[0] == transactions[5]
    assert data[1] == transactions[6]

    # Test - Get transactions before a date
    response = state.client.get(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        headers=make_headers(state.user),
        params={"before": _date_std_isoformat(2024, 12, 11, tzinfo=datetime.timezone.utc)}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    assert data[0] == transactions[0]
    assert data[1] == transactions[1]
    assert data[2] == transactions[2]

    # Test - Get transactions in a range of dates
    response = state.client.get(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        headers=make_headers(state.user),
        params={
            "after": _date_std_isoformat(2024, 3, 1, tzinfo=datetime.timezone.utc),
            "before": _date_std_isoformat(2025, 8, 6, tzinfo=datetime.timezone.utc),
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4

    assert data[0] == transactions[1]
    assert data[1] == transactions[2]
    assert data[2] == transactions[3]
    assert data[3] == transactions[4]


def test_balance(state: RouterTestState):
    assert state.user is not None

    response = state.client.get(
        "/accounts/{account_id}/balance".format(account_id=state.baton["account"].id),
        headers=make_headers(state.user),
    )

    assert response.status_code == 200
    assert response.json()["balance"] == state.baton["balance"]  # state.baton["balance"] set by previous test

def test_log_transaction(state: RouterTestState):
    assert state.user is not None

    response = state.client.post(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        json={
            "amount": 250,
            "description": "Groceries",
            "date": _date_std_isoformat(2025, 8, 4, 12, 14, 23, tzinfo=datetime.timezone.utc),
        },
        headers=make_headers(state.user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("amount") == 250
    assert data.get("description") == "Groceries"
    assert data.get("date") == _date_std_isoformat(2025, 8, 4, 12, 14, 23, tzinfo=datetime.timezone.utc)


def test_get_transaction(state: RouterTestState):
    assert state.user is not None

    response = state.client.post(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        json={
            "amount": 250,
            "date": _date_std_isoformat(2022, 8, 4, 12, 14, 23, tzinfo=datetime.timezone.utc),
        },
        headers=make_headers(state.user),
    )
    assert response.status_code == 200
    data = response.json()

    response = state.client.get(
        "/accounts/{account_id}/transactions/{transaction_id}".format(
            account_id=state.baton["account"].id,
            transaction_id=data["id"],
        ),
        headers=make_headers(state.user),
    )
    assert response.status_code == 200
    assert response.json() == data


def test_edit_transaction(state: RouterTestState):
    assert state.user is not None

    response = state.client.post(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        json={
            "amount": 2150,
            "description": "old description",
            "date": _date_std_isoformat(2021, 8, 3, 12, 14, 23, tzinfo=datetime.timezone.utc),
        },
        headers=make_headers(state.user),
    )
    assert response.status_code == 200
    transaction = response.json()

    # Test - Basic amount update
    response = state.client.patch(
        "/accounts/{account_id}/transactions/{transaction_id}".format(
            account_id=state.baton["account"].id,
            transaction_id=transaction["id"],
        ),
        headers=make_headers(state.user),
        json={"amount": 2000}
    )

    assert response.status_code == 200
    data = response.json()

    assert data.get("id") == transaction["id"]
    assert data.get("amount") == 2000

    transaction = data

    # Test - unset field
    response = state.client.patch(
        "/accounts/{account_id}/transactions/{transaction_id}".format(
            account_id=state.baton["account"].id,
            transaction_id=transaction["id"],
        ),
        headers=make_headers(state.user),
        json={"description": None}
    )
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data.get("description") == None

def test_delete_transaction(state: RouterTestState):
    assert state.user is not None

    response = state.client.post(
        "/accounts/{account_id}/transactions".format(account_id=state.baton["account"].id),
        json={
            "amount": 2150,
            "description": "old description",
            "date": _date_std_isoformat(2021, 8, 3, 12, 14, 23, tzinfo=datetime.timezone.utc),
        },
        headers=make_headers(state.user),
    )
    assert response.status_code == 200
    transaction = response.json()

    # Test - Basic transaction deletion
    response = state.client.delete(
        "/accounts/{account_id}/transactions/{transaction_id}".format(
            account_id=state.baton["account"].id,
            transaction_id=transaction["id"],
        ),
        headers=make_headers(state.user),
    )

    assert response.status_code == 204

    response = state.client.get(
        "/accounts/{account_id}/transactions/{transaction_id}".format(
            account_id=state.baton["account"].id,
            transaction_id=transaction["id"],
        ),
        headers=make_headers(state.user),
    )

    assert response.status_code == 404

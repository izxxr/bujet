# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from pydantic import UUID4
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from core.deps import require_auth
from core import schemas, models

__all__ = (
    "accounts",
)

accounts = APIRouter(prefix="/accounts")

@accounts.post("/", dependencies=[Depends(require_auth)])
async def create_account(request: Request, data: schemas.CreateAccountJSON) -> schemas.FinancialAccount:
    """Create a financial account."""
    acc = data.to_db_model(user=request.state.user)
    await acc.save()
    return schemas.FinancialAccount.from_db_model(acc, user=request.state.user)

@accounts.get("/", dependencies=[Depends(require_auth)])
async def get_all_accounts(request: Request) -> list[schemas.FinancialAccount]:
    """Get all accounts associated to requesting user."""
    accs = await models.FinancialAccount.filter(user=request.state.user).all()
    return [schemas.FinancialAccount.from_db_model(a, user=request.state.user) for a in accs]

@accounts.get("/{account_id}", dependencies=[Depends(require_auth)])
async def get_account(request: Request, account_id: UUID4) -> schemas.FinancialAccount:
    """Get a specific account by its ID."""
    acc = await models.FinancialAccount.filter(id=account_id, user=request.state.user).first()

    if acc is None:
        raise HTTPException(404, "Account not found")

    return schemas.FinancialAccount.from_db_model(acc, user=request.state.user)

@accounts.patch("/{account_id}", dependencies=[Depends(require_auth)])
async def edit_account(request: Request, account_id: UUID4, data: schemas.EditAccountJSON) -> schemas.FinancialAccount:
    """Update information of a specific account."""
    acc = await models.FinancialAccount.filter(id=account_id, user=request.state.user).first()

    if acc is None:
        raise HTTPException(404, "Account not found")

    acc.update_from_dict(data.to_dict())  # type: ignore
    await acc.save()

    return schemas.FinancialAccount.from_db_model(acc, user=request.state.user)

@accounts.delete("/{account_id}", dependencies=[Depends(require_auth)])
async def delete_account(request: Request, account_id: UUID4) -> Response:
    """Delete an account and associated transactions.

    Returns 204 No Content on success.
    """
    acc = await models.FinancialAccount.filter(id=account_id, user=request.state.user).first()

    if acc is None:
        raise HTTPException(404, "Account not found")
    
    await acc.delete()
    return Response(None, 204)

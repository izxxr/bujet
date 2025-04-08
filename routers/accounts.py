# Copyright (C) Izhar Ahmad 2025-2026 - under the MIT license

from __future__ import annotations

from tortoise.functions import Sum
from pydantic import UUID4, AwareDatetime
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from core.deps import require_auth
from core import schemas, models

__all__ = (
    "accounts",
)

async def fetch_account(request: Request, account_id: UUID4) -> models.FinancialAccount:
    """Fetches the given account using the given ID.

    If fetch_related=True, the related fields (user) are also
    fetched. Defaults to False.
    """
    acc = await models.FinancialAccount.filter(id=account_id, user=request.state.user).first()

    if acc is None:
        raise HTTPException(404, "Account not found")

    return acc

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
    acc = await fetch_account(request, account_id)
    return schemas.FinancialAccount.from_db_model(acc, user=request.state.user)

@accounts.patch("/{account_id}", dependencies=[Depends(require_auth)])
async def edit_account(request: Request, account_id: UUID4, data: schemas.EditAccountJSON) -> schemas.FinancialAccount:
    """Update information of a specific account.

    Returns the updated account on success.
    """
    acc = await fetch_account(request, account_id)

    acc.update_from_dict(data.to_dict())  # type: ignore
    await acc.save()

    return schemas.FinancialAccount.from_db_model(acc, user=request.state.user)

@accounts.delete("/{account_id}", dependencies=[Depends(require_auth)])
async def delete_account(request: Request, account_id: UUID4) -> Response:
    """Delete an account and associated transactions.

    Returns 204 No Content on success.
    """
    acc = await fetch_account(request, account_id)
    
    await acc.delete()
    return Response(None, 204)

# -- Transactions --

@accounts.post("/{account_id}/transactions", dependencies=[Depends(require_auth)])
async def log_transaction(request: Request, account_id: UUID4, data: schemas.LogTransactionJSON) -> schemas.Transaction:
    """Log a transaction in the specified financial account."""
    acc = await fetch_account(request, account_id)
    transaction = data.to_db_model(acc)

    await transaction.save()
    return schemas.Transaction.from_db_model(transaction, acc)

@accounts.get("/{account_id}/transactions-count", dependencies=[Depends(require_auth)])
async def count_transactions(request: Request, account_id: UUID4) -> schemas.CountTransactionsResponse:
    """Returns the total number of transactions that the account has."""
    acc = await fetch_account(request, account_id)
    count = await models.Transaction.filter(account=acc).count()
    return schemas.CountTransactionsResponse(count=count)

@accounts.get("/{account_id}/transactions", dependencies=[Depends(require_auth)])
async def list_transactions(
    request: Request,
    account_id: UUID4,
    after: AwareDatetime | None = None,
    before: AwareDatetime | None = None,
    limit: int = 20,
) -> list[schemas.Transaction]:
    """Log a transaction in the specified financial account.

    This endpoint supports paginating transactions using before,
    after, and limit parameters. Pagination works as follows:
     
    - before and after determine the time before or after which the
      transactions are returned respectively.

    - limit allows changing the number of transactions per page (request).

    - If none of after/before is provided, the `limit` number of latest
      transactions are returned.

    - Both before and after can be set to obtain transactions in a range
      of dates.

    Query Parameters
    ~~~~~~~~~~~~~~~~
    after:
        If provided, transactions after this time will be returned.
    before:
        If provided, transactions before this time will be returned.
    limit:
        The number of transactions to return in response. Defaults to
        20 and capped at 40 per request.
    """
    if limit > 40:
        raise HTTPException(422, "limit cannot be greater than 40")
    
    kwargs = {}

    if after:
        kwargs["date__gte"] = after
    if before:
        kwargs["date__lte"] = before

    acc = await fetch_account(request, account_id)
    transactions = await models.Transaction.filter(**kwargs, account=acc).limit(limit).order_by("-date")

    return [schemas.Transaction.from_db_model(t, acc) for t in transactions]

@accounts.get("/{account_id}/transactions/{transaction_id}", dependencies=[Depends(require_auth)])
async def get_transaction(request: Request, account_id: UUID4, transaction_id: UUID4) -> schemas.Transaction:
    """Get a specific transaction by its ID."""
    acc = await fetch_account(request, account_id)
    transaction = await models.Transaction.filter(id=transaction_id, account=acc).first()

    if transaction is None:
        raise HTTPException(404, "Transaction not found")

    return schemas.Transaction.from_db_model(transaction, acc)

@accounts.delete("/{account_id}/transactions/{transaction_id}", dependencies=[Depends(require_auth)])
async def delete_transaction(request: Request, account_id: UUID4, transaction_id: UUID4) -> Response:
    """Log a transaction in the specified financial account.
    
    On successful deletion, 204 No Content response is returned.
    """
    acc = await fetch_account(request, account_id)
    transaction = await models.Transaction.filter(id=transaction_id, account=acc).first()

    if transaction is None:
        raise HTTPException(404, "Transaction not found")

    await transaction.delete()
    return Response(None, 204)

@accounts.patch("/{account_id}/transactions/{transaction_id}", dependencies=[Depends(require_auth)])
async def edit_transaction(request: Request, account_id: UUID4, transaction_id: UUID4, data: schemas.EditTransactionJSON) -> schemas.Transaction:
    """Edit a transaction's information.

    Returns the updated transaction on success.
    """
    acc = await fetch_account(request, account_id)
    transaction = await models.Transaction.filter(id=transaction_id, account=acc).first()

    if transaction is None:
        raise HTTPException(404, "Transaction not found")

    transaction.update_from_dict(data.to_dict())  # type: ignore
    await transaction.save()

    return schemas.Transaction.from_db_model(transaction, acc)

# Balance calculation

@accounts.get("/{account_id}/balance", dependencies=[Depends(require_auth)])
async def calculate_balance(request: Request, account_id: UUID4) -> schemas.CalculateBalanceResponse:
    """Calculates the balance of the account.
    
    Like transactions, the balance is also returned in minor units format
    and must be divided by 100 to obtain the actual balance value.
    """
    acc = await fetch_account(request, account_id)
    vals = await models.Transaction.filter(account=acc).annotate(balance=Sum("amount")).first()

    # Transaction.balance is added by annotate()
    return schemas.CalculateBalanceResponse(balance=vals.balance or 0)  # type: ignore

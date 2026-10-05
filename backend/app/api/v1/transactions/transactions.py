from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin, get_current_user
from app.database.connection.conn import get_db
from app.models.enums.TransactionEnums import TransactionStatus
from app.models.users import User
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.transaction_schema import TransactionResponse
from app.services.transaction import transaction_service

router = APIRouter()

def _raise(exc: Exception):
    code = (
        404 if isinstance(exc, LookupError)
        else 403 if isinstance(exc, PermissionError)
        else 400 if isinstance(exc, ValueError)
        else 500
    )
    raise HTTPException(status_code=code, detail=str(exc)) from exc


# --- User Transactions ---

@router.get(
    "/transactions",
    response_model=PaginatedResponse[TransactionResponse],
    tags=["Transactions"],
    summary="List transactions where current user is buyer or seller",
)
def list_my_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: TransactionStatus | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        data, pagination = transaction_service.list_user_transactions(
            db, user, page, limit, status
        )
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/transactions/buy",
    response_model=PaginatedResponse[TransactionResponse],
    tags=["Transactions"],
    summary="List purchase transactions where current user is buyer",
)
def list_buy_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: TransactionStatus | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        data, pagination = transaction_service.list_buyer_transactions(
            db, user, page, limit, status
        )
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/transactions/sell",
    response_model=PaginatedResponse[TransactionResponse],
    tags=["Transactions"],
    summary="List sale transactions where current user is seller",
)
def list_sell_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: TransactionStatus | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        data, pagination = transaction_service.list_seller_transactions(
            db, user, page, limit, status
        )
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    tags=["Transactions"],
    summary="Get transaction details by ID",
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return transaction_service.get_user_transaction(db, transaction_id, user)
    except Exception as exc:
        _raise(exc)


# --- Admin Transactions ---

@router.get(
    "/admin/transactions",
    response_model=PaginatedResponse[TransactionResponse],
    tags=["Admin Transactions"],
    summary="Admin list all transactions",
)
def admin_list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    buyer_id: int | None = Query(None),
    seller_id: int | None = Query(None),
    status: TransactionStatus | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        data, pagination = transaction_service.list_admin_transactions(
            db, page, limit, buyer_id, seller_id, status
        )
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get(
    "/admin/transactions/{transaction_id}",
    response_model=TransactionResponse,
    tags=["Admin Transactions"],
    summary="Admin get transaction by ID",
)
def admin_get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return transaction_service.get_admin_transaction(db, transaction_id)
    except Exception as exc:
        _raise(exc)

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin, get_current_seller, get_current_user
from app.database.connection.conn import get_db
from app.models.enums.OrderEnums import OrderStatus
from app.models.users import User
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.order_schema import OrderCreate, OrderCreateRequest, OrderResponse, OrderStatusUpdate
from app.services.orders import order_service

router = APIRouter()

def _raise(exc: Exception):
    code = 404 if isinstance(exc, LookupError) else 403 if isinstance(exc, PermissionError) else 409 if isinstance(exc, ValueError) else 400
    raise HTTPException(code, str(exc)) from exc


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order_from_body(payload: OrderCreateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        values = payload.model_dump(exclude={"listing_id"})
        return order_service.create_order(db, payload.listing_id, user, values)
    except Exception as exc:
        _raise(exc)


@router.post("/orders/listings/{listing_id}", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(listing_id: int, payload: OrderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return order_service.create_order(db, listing_id, user, payload.model_dump())
    except Exception as exc:
        _raise(exc)


@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return order_service.get_order_for_user(db, order_id, user)
    except Exception as exc:
        _raise(exc)


@router.get("/buyer/orders", response_model=PaginatedResponse[OrderResponse], tags=["Buyer Orders"])
def list_buyer_orders(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), order_status: OrderStatus | None = Query(None, alias="status"), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        data, pagination = order_service.list_buyer_orders(db, user, page, limit, order_status)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.patch("/buyer/orders/{order_id}/cancel", response_model=OrderResponse, tags=["Buyer Orders"])
def cancel_buyer_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return order_service.cancel_buyer_order(db, order_id, user)
    except Exception as exc:
        _raise(exc)


@router.get("/seller/orders", response_model=PaginatedResponse[OrderResponse], tags=["Seller Orders"])
def list_seller_orders(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), order_status: OrderStatus | None = Query(None, alias="status"), db: Session = Depends(get_db), user: User = Depends(get_current_seller)):
    try:
        data, pagination = order_service.list_seller_orders(db, user, page, limit, order_status)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.patch("/seller/orders/{order_id}/accept", response_model=OrderResponse, tags=["Seller Orders"])
def accept_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_seller)):
    try:
        return order_service.accept_order(db, order_id, user)
    except Exception as exc:
        _raise(exc)


@router.patch("/seller/orders/{order_id}/reject", response_model=OrderResponse, tags=["Seller Orders"])
def reject_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_seller)):
    try:
        return order_service.reject_order(db, order_id, user)
    except Exception as exc:
        _raise(exc)


@router.patch("/seller/orders/{order_id}/status", response_model=OrderResponse, tags=["Seller Orders"])
def update_seller_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_seller)):
    try:
        return order_service.update_seller_order_status(db, order_id, user, payload.status)
    except Exception as exc:
        _raise(exc)


@router.get("/admin/orders", response_model=PaginatedResponse[OrderResponse], tags=["Admin Orders"])
def list_admin_orders(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), order_status: OrderStatus | None = Query(None, alias="status"), db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    data, pagination = order_service.list_admin_orders(db, page, limit, order_status)
    return {"data": data, "pagination": pagination}


@router.get("/admin/orders/{order_id}", response_model=OrderResponse, tags=["Admin Orders"])
def get_admin_order(order_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        return order_service.get_order_for_user(db, order_id, admin)
    except Exception as exc:
        _raise(exc)


@router.patch("/admin/orders/{order_id}/status", response_model=OrderResponse, tags=["Admin Orders"])
def update_admin_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        return order_service.update_admin_order_status(db, order_id, admin, payload.status)
    except Exception as exc:
        _raise(exc)

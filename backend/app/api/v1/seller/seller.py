from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_seller
from app.database.connection.conn import get_db
from app.models.inquiries import InquiryStatus
from app.models.users import User
from app.schemas.buyer_schema import InquiryMessageCreate, InquiryMessageResponse
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.seller_schema import (
    SellerInquiryDetailResponse,
    SellerInquiryResponse,
    SellerInquiryStatusUpdate,
)
from app.services.seller import seller_service

router = APIRouter()

def _raise(exc: Exception):
    code = 404 if isinstance(exc, LookupError) else 403 if isinstance(exc, PermissionError) else 409 if isinstance(exc, ValueError) else 400
    raise HTTPException(code, str(exc)) from exc


@router.get("/seller/inquiries", response_model=PaginatedResponse[SellerInquiryResponse], tags=["Seller Inquiries"])
def list_inquiries(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    inquiry_status: InquiryStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_seller),
):
    try:
        data, pagination = seller_service.list_seller_inquiries(
            db, user, page, limit, inquiry_status
        )
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get("/seller/inquiries/{inquiry_id}", response_model=SellerInquiryDetailResponse, tags=["Seller Inquiries"])
def get_inquiry(inquiry_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_seller)):
    try:
        return seller_service.get_seller_inquiry(db, inquiry_id, user)
    except Exception as exc:
        _raise(exc)


@router.patch("/seller/inquiries/{inquiry_id}/status", response_model=SellerInquiryDetailResponse, tags=["Seller Inquiries"])
def update_status(inquiry_id: int, payload: SellerInquiryStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_seller)):
    try:
        return seller_service.update_inquiry_status(db, inquiry_id, user, payload.status)
    except Exception as exc:
        _raise(exc)


@router.post("/seller/inquiries/{inquiry_id}/messages", response_model=InquiryMessageResponse, status_code=status.HTTP_201_CREATED, tags=["Seller Inquiries"])
def reply_to_buyer(inquiry_id: int, payload: InquiryMessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_seller)):
    try:
        return seller_service.send_seller_message(db, inquiry_id, user, payload.model_dump())
    except Exception as exc:
        _raise(exc)

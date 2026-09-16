from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.models.enums.TransactionEnums import TransactionStatus
from app.models.users import User
from app.schemas.buyer_schema import (
    BuyerDashboardResponse,
    BuyerInquiryCreate,
    BuyerInquiryDetailResponse,
    BuyerInquiryResponse,
    BuyerPurchaseResponse,
    InquiryMessageCreate,
    InquiryMessageResponse,
    RecentlyViewedListingResponse,
)
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.marketplace_schema import FavoriteResponse, ListingResponseSecond
from app.services.buyer import buyer_service

router = APIRouter()

def _raise(exc: Exception):
    code = 404 if isinstance(exc, LookupError) else 403 if isinstance(exc, PermissionError) else 409 if isinstance(exc, ValueError) else 400
    raise HTTPException(code, str(exc)) from exc


@router.get("/buyer/listings/{listing_id}", response_model=ListingResponseSecond, tags=["Buyer Discovery"])
def view_listing(listing_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.get_listing_and_record_view(db, listing_id, user)
    except Exception as exc:
        _raise(exc)


@router.get("/buyer/recently-viewed", response_model=list[RecentlyViewedListingResponse], tags=["Buyer Discovery"])
def recently_viewed(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.list_recent_views(db, user, limit)
    except Exception as exc:
        _raise(exc)


@router.get("/buyer/interested-cars", response_model=list[FavoriteResponse], tags=["Buyer Discovery"])
def interested_cars(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.list_interested_cars(db, user)
    except Exception as exc:
        _raise(exc)


@router.post("/buyer/listings/{listing_id}/inquiries", response_model=BuyerInquiryDetailResponse, status_code=status.HTTP_201_CREATED, tags=["Buyer Inquiries"])
def create_inquiry(listing_id: int, payload: BuyerInquiryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.create_inquiry(db, listing_id, user, payload.model_dump())
    except Exception as exc:
        _raise(exc)


@router.get("/buyer/inquiries", response_model=PaginatedResponse[BuyerInquiryResponse], tags=["Buyer Inquiries"])
def list_inquiries(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        data, pagination = buyer_service.list_buyer_inquiries(db, user, page, limit)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get("/buyer/inquiries/{inquiry_id}", response_model=BuyerInquiryDetailResponse, tags=["Buyer Inquiries"])
def get_inquiry(inquiry_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.get_buyer_inquiry(db, inquiry_id, user)
    except Exception as exc:
        _raise(exc)


@router.get("/inquiries/{inquiry_id}/messages", response_model=list[InquiryMessageResponse], tags=["Inquiry Messages"])
def list_messages(inquiry_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.list_inquiry_messages(db, inquiry_id, user)
    except Exception as exc:
        _raise(exc)


@router.post("/inquiries/{inquiry_id}/messages", response_model=InquiryMessageResponse, status_code=status.HTTP_201_CREATED, tags=["Inquiry Messages"])
def send_message(inquiry_id: int, payload: InquiryMessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.send_inquiry_message(db, inquiry_id, user, payload.model_dump())
    except Exception as exc:
        _raise(exc)


@router.get("/buyer/purchases", response_model=PaginatedResponse[BuyerPurchaseResponse], tags=["Buyer Purchases"])
def list_purchases(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), transaction_status: TransactionStatus | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        data, pagination = buyer_service.list_purchases(db, user, page, limit, transaction_status)
        return {"data": data, "pagination": pagination}
    except Exception as exc:
        _raise(exc)


@router.get("/buyer/purchases/{transaction_id}", response_model=BuyerPurchaseResponse, tags=["Buyer Purchases"])
def get_purchase(transaction_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.get_purchase(db, transaction_id, user)
    except Exception as exc:
        _raise(exc)


@router.get("/buyer/dashboard", response_model=BuyerDashboardResponse, tags=["Buyer Dashboard"])
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return buyer_service.get_dashboard(db, user)
    except Exception as exc:
        _raise(exc)

import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.payment_schema import PaymentCreate, PaymentResponse, PaymentStatusResponse, PaymentVerify
from app.services.payments import payment_service
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

router = APIRouter()

def _raise(exc: Exception):
    code = 404 if isinstance(exc, LookupError) else 403 if isinstance(exc, PermissionError) else 422 if isinstance(exc, payment_service.PaymentAmountLimitError) else 409 if isinstance(exc, ValueError) else 503 if isinstance(exc, RuntimeError) else 400
    raise HTTPException(code, str(exc)) from exc

@router.post("/payments", response_model=PaymentStatusResponse, status_code=status.HTTP_201_CREATED, tags=["Payments"])
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        payment = payment_service.create_payment(db, payload.order_id, payload.payment_method, user)
        response = PaymentStatusResponse.model_validate(payment)
        response.razorpay_key_id = os.getenv("RAZORPAY_KEY_ID")
        return response
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.get("/payments/{payment_id}", response_model=PaymentResponse, tags=["Payments"])
def get_payment(payment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return payment_service.get_payment_for_user(db, payment_id, user)
    except Exception as exc:
        _raise(exc)


@router.get("/payments/order/{order_id}", response_model=PaymentResponse, tags=["Payments"])
def get_order_payment(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return payment_service.get_order_payment(db, order_id, user)
    except Exception as exc:
        _raise(exc)


@router.post("/payments/{payment_id}/verify", response_model=PaymentResponse, tags=["Payments"])
def verify_payment(payment_id: int, payload: PaymentVerify, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return payment_service.verify_payment(db, payment_id, payload.model_dump(), user)
    except Exception as exc:
        db.rollback()
        _raise(exc)


@router.post("/payments/webhook", response_model=PaymentResponse | None, tags=["Payments"])
async def razorpay_webhook(request: Request, x_razorpay_signature: str | None = Header(default=None), db: Session = Depends(get_db)):
    try:
        return payment_service.process_webhook(db, await request.body(), x_razorpay_signature)
    except Exception as exc:
        db.rollback()
        _raise(exc)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_seller
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.dashboard_schema import SellerDashboardResponse
from app.services.dashboard import dashboard_service

router = APIRouter()

@router.get("/seller/dashboard",response_model=SellerDashboardResponse,summary="Get seller dashboard metrics",tags=["Seller Dashboard"])
def get_seller_dashboard(db: Session = Depends(get_db),current_user: User = Depends(get_current_seller)):
    return dashboard_service.get_seller_dashboard(db, current_user)

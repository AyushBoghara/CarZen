from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.models.enums.UserRoles import UserRoles
from app.models.users import User
from app.schemas.dashboard_schema import SellerDashboardResponse
from app.services.dashboard import dashboard_service

router = APIRouter()

@router.get("/seller/dashboard",response_model=SellerDashboardResponse,summary="Get seller dashboard metrics",tags=["Seller Dashboard"])
def get_seller_dashboard(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    
    if current_user.role not in {UserRoles.SELLER,UserRoles.USER, UserRoles.RESELLER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Seller or reseller access required.")

    return dashboard_service.get_seller_dashboard(db, current_user)

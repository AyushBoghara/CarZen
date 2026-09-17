from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_admin, get_current_user
from app.database.connection.conn import get_db
from app.models.enums.ReportEnums import ReportStatus
from app.models.users import User
from app.schemas.cars_schema import PaginatedResponse
from app.schemas.report_schema import ReportCreate, ReportResponse, ReportStatusUpdate
from app.services.reports import report_service

router = APIRouter()

def _raise(exc: Exception):
    code = 404 if isinstance(exc, LookupError) else 403 if isinstance(exc, PermissionError) else 409 if isinstance(exc, ValueError) else 400
    raise HTTPException(code, str(exc)) from exc


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED, tags=["Reports"])
def create_report(payload: ReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return report_service.create_report(db, payload.model_dump(), user)
    except Exception as exc:
        db.rollback()
        _raise(exc)

@router.get("/reports/my", response_model=PaginatedResponse[ReportResponse], tags=["Reports"])
def list_my_reports(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data, pagination = report_service.list_my_reports(db, user, page, limit)
    return {"data": data, "pagination": pagination}


@router.get("/reports/{report_id}", response_model=ReportResponse, tags=["Reports"])
def get_report(report_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return report_service.get_my_report(db, report_id, user)
    except Exception as exc:
        _raise(exc)


@router.get("/admin/reports", response_model=PaginatedResponse[ReportResponse], tags=["Admin Reports"])
def list_reports(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), report_status: ReportStatus | None = Query(None, alias="status"), db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    data, pagination = report_service.list_reports(db, page, limit, report_status)
    return {"data": data, "pagination": pagination}


@router.get("/admin/reports/{report_id}", response_model=ReportResponse, tags=["Admin Reports"])
def get_admin_report(report_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    try:
        return report_service._get_report(db, report_id)
    except Exception as exc:
        _raise(exc)


@router.patch("/admin/reports/{report_id}/status", response_model=ReportResponse, tags=["Admin Reports"])
def update_report_status(report_id: int, payload: ReportStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        return report_service.update_status(db, report_id, payload.model_dump(), admin)
    except Exception as exc:
        db.rollback()
        _raise(exc)
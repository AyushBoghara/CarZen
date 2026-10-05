from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.enums.OrderEnums import NotificationType
from app.models.enums.ReportEnums import ReportStatus
from app.models.enums.UserRoles import UserRoles
from app.models.listings import Listings
from app.models.reports import Reports
from app.models.users import User
from app.services.car.catalog_service import paginate
from app.services.notifications import notification_service


def create_report(db: Session, values: dict, reporter: User) -> Reports:
    _validate_target(db, values.get("listing_id"), values.get("car_id"))
    duplicate = db.query(Reports).filter(
        Reports.reporter_id == reporter.id,
        Reports.listing_id == values.get("listing_id"),
        Reports.car_id == values.get("car_id"),
        Reports.status.in_([ReportStatus.PENDING, ReportStatus.UNDER_REVIEW]),
    ).first()
    
    if duplicate:
        raise ValueError("You already have an open report for this target.")
    
    report = Reports(reporter_id=reporter.id, **values)
    
    db.add(report)
    db.flush()
    for (admin_id,) in db.query(User.id).filter(User.role == UserRoles.ADMIN, User.deleted_at.is_(None)):
        notification_service.create_notification(
            db, admin_id, NotificationType.ADMIN, "New marketplace report",
            "A listing or car has been reported for review.", report.id, "report",
        )
        
    notification_service.create_notification(
        db, reporter.id, NotificationType.SYSTEM, "Report submitted",
        "Your report has been submitted for administrator review.", report.id, "report",
    )
    
    db.commit()
    db.refresh(report)
    return report


def get_my_report(db: Session, report_id: int, reporter: User) -> Reports:
    report = _get_report(db, report_id)
    if report.reporter_id != reporter.id:
        raise PermissionError("You do not have access to this report.")
    return report


def list_my_reports(db: Session, reporter: User, page: int, limit: int):
    query = db.query(Reports).filter(Reports.reporter_id == reporter.id)
    return paginate(query.order_by(Reports.created_at.desc(), Reports.id.desc()), page, limit)


def list_reports(db: Session, page: int, limit: int, report_status: ReportStatus | None = None):
    query = db.query(Reports)
    if report_status:
        query = query.filter(Reports.status == report_status)
    return paginate(query.order_by(Reports.created_at.desc(), Reports.id.desc()), page, limit)


def update_status(db: Session, report_id: int, values: dict, admin: User) -> Reports:
    report = _get_report(db, report_id)
    
    target = values["status"]
    if report.status in {ReportStatus.RESOLVED, ReportStatus.REJECTED}:
        raise ValueError("Closed reports cannot be updated.")
    
    report.status = target
    report.admin_note = values.get("admin_note")
    
    if target in {ReportStatus.RESOLVED, ReportStatus.REJECTED}:
        report.resolved_at = datetime.now(timezone.utc)
        report.resolved_by_id = admin.id
        
    notification_service.create_notification(
        db, report.reporter_id, NotificationType.ADMIN, f"Report {target.value}",
        "An administrator updated the status of your marketplace report.", report.id, "report",
    )
    
    db.commit()
    db.refresh(report)
    return report


def _get_report(db: Session, report_id: int) -> Reports:
    report = db.get(Reports, report_id)
    if not report:
        raise LookupError("Report not found.")
    return report


def _validate_target(db: Session, listing_id: int | None, car_id: int | None) -> None:
    listing = None
    if listing_id is not None:
        listing = db.get(Listings, listing_id)
        
        if not listing or listing.deleted_at is not None:
            raise LookupError("Listing not found.")
        
    if car_id is not None:
        from app.models.cars import Cars
        car = db.get(Cars, car_id)
        
        if not car or car.deleted_at is not None:
            raise LookupError("Car not found.")
        
        if listing and listing.car_id != car_id:
            raise ValueError("The listing does not belong to the supplied car.")

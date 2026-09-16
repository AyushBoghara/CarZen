from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.cars import Cars
from app.models.enums.CarEnums import CarApprovalStatus
from app.models.enums.ListingEnums import ListingStatus
from app.models.inquiries import Inquiries
from app.models.listings import Listings
from app.models.users import User


def get_seller_dashboard(db: Session, seller: User) -> dict[str, int]:
    
    base_listings = db.query(Listings).filter(
        Listings.seller_id == seller.id,
        Listings.deleted_at.is_(None),
    )

    total_listings = base_listings.count()
    
    active_listings = base_listings.filter(Listings.listing_status == ListingStatus.ACTIVE).count()

    pending_approvals = db.query(Cars).filter(
        Cars.owner_id == seller.id,
        Cars.deleted_at.is_(None),
        Cars.approval_status == CarApprovalStatus.PENDING_APPROVAL,
    ).count()

    sold_cars = (
        db.query(func.count(func.distinct(Cars.id)))
        .outerjoin(
            Listings,
            and_(
                Listings.car_id == Cars.id,
                Listings.seller_id == seller.id,
                Listings.deleted_at.is_(None),
            ),
        )
        .filter(
            Cars.owner_id == seller.id,
            Cars.deleted_at.is_(None),
            or_(
                Cars.approval_status == CarApprovalStatus.SOLD,
                Listings.listing_status == ListingStatus.SOLD,
            ),
        )
        .scalar()
        or 0
    )

    inquiries = db.query(Inquiries).filter(Inquiries.seller_id == seller.id).count()

    return {
        "total_listings": total_listings,
        "active_listings": active_listings,
        "pending_approvals": pending_approvals,
        "sold_cars": sold_cars,
        "inquiries": inquiries,
    }

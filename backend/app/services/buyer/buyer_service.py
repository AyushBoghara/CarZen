from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload

from app.models.car_models import CarModels
from app.models.car_variants import CarVariants
from app.models.cars import Cars
from app.models.enums.ListingEnums import ListingStatus
from app.models.enums.OrderEnums import NotificationType
from app.models.enums.TransactionEnums import TransactionStatus
from app.models.enums.UserRoles import UserRoles
from app.models.favorites import Favorites
from app.models.inquiries import Inquiries, InquiryStatus
from app.models.inquiry_messages import InquiryMessages
from app.models.listing_views import ListingViews
from app.models.listings import Listings
from app.models.transactions import Transactions
from app.models.users import User
from app.services.car import marketplace_service
from app.services.car.catalog_service import paginate
from app.services.notifications import notification_service


BUYER_ROLES = {UserRoles.USER}


def ensure_buyer(user: User) -> None:
    if user.role not in BUYER_ROLES:
        raise PermissionError("Buyer or user access required.")


def get_listing_and_record_view(db: Session, listing_id: int, buyer: User) -> Listings:
    
    ensure_buyer(buyer)
    
    listing = marketplace_service.get_listings(db, listing_id)
    
    view = db.query(ListingViews).filter(
        ListingViews.listing_id == listing.id,
        ListingViews.buyer_id == buyer.id,
    ).first()
    
    if view:
        view.viewed_at = datetime.now(timezone.utc)
    else:
        db.add(ListingViews(listing_id=listing.id, buyer_id=buyer.id))
        
    listing.views_count = (listing.views_count or 0) + 1
    db.commit()
    return listing


def list_recent_views(db: Session, buyer: User, limit: int) -> list[ListingViews]:
    ensure_buyer(buyer)
    return (
        db.query(ListingViews)
        .join(ListingViews.listing)
        .options(*_listing_detail_loads(ListingViews.listing))
        .filter(ListingViews.buyer_id == buyer.id, Listings.deleted_at.is_(None))
        .order_by(ListingViews.viewed_at.desc())
        .limit(limit)
        .all()
    )


def list_interested_cars(db: Session, buyer: User) -> list[Favorites]:
    ensure_buyer(buyer)
    return (
        db.query(Favorites)
        .join(Favorites.car)
        .options(
            selectinload(Favorites.car)
            .selectinload(Cars.variant)
            .selectinload(CarVariants.model)
            .selectinload(CarModels.brand),
            selectinload(Favorites.car).selectinload(Cars.media),
            selectinload(Favorites.car).selectinload(Cars.features),
        )
        .filter(Favorites.user_id == buyer.id, Cars.deleted_at.is_(None))
        .order_by(Favorites.created_at.desc())
        .all()
    )


def create_inquiry(db: Session, listing_id: int, buyer: User, values: dict) -> Inquiries:
    ensure_buyer(buyer)
    listing = marketplace_service.get_listing(db, listing_id)
    if listing.seller_id == buyer.id:
        raise ValueError("You cannot send an inquiry for your own listing.")

    inquiry = Inquiries(
        listing_id=listing.id,
        buyer_id=buyer.id,
        seller_id=listing.seller_id,
        **values,
    )
    db.add(inquiry)
    db.flush()
    notification_service.create_notification(
        db,
        listing.seller_id,
        NotificationType.INQUIRY,
        "New buyer inquiry",
        f"A buyer sent an inquiry for {listing.title}.",
        inquiry.id,
        "inquiry",
    )
    db.commit()
    return get_buyer_inquiry(db, inquiry.id, buyer)


def list_buyer_inquiries(db: Session, buyer: User, page: int, limit: int):
    ensure_buyer(buyer)
    query = _inquiry_query(db).filter(Inquiries.buyer_id == buyer.id)
    return paginate(query.order_by(Inquiries.updated_at.desc(), Inquiries.id.desc()), page, limit)


def get_buyer_inquiry(db: Session, inquiry_id: int, buyer: User) -> Inquiries:
    ensure_buyer(buyer)
    inquiry = _inquiry_query(db, include_messages=True).filter(
        Inquiries.id == inquiry_id,
        Inquiries.buyer_id == buyer.id,
    ).first()
    
    if not inquiry:
        raise LookupError("Inquiry not found.")
    return inquiry


def list_inquiry_messages(db: Session, inquiry_id: int, user: User) -> list[InquiryMessages]:
    inquiry = _get_inquiry_participant(db, inquiry_id, user)
    return sorted(inquiry.messages, key=lambda message: (message.created_at, message.id))


def send_inquiry_message(
    db: Session,
    inquiry_id: int,
    user: User,
    values: dict,
) -> InquiryMessages:
    inquiry = _get_inquiry_participant(db, inquiry_id, user)
    message = InquiryMessages(inquiry_id=inquiry.id, sender_id=user.id, **values)
    if user.id == inquiry.seller_id and inquiry.status == InquiryStatus.OPEN:
        inquiry.status = InquiryStatus.CONTACTED
    db.add(message)
    recipient_id = inquiry.buyer_id if user.id == inquiry.seller_id else inquiry.seller_id
    notification_service.create_notification(
        db,
        recipient_id,
        NotificationType.INQUIRY,
        "New inquiry message",
        "You received a new message in an inquiry conversation.",
        inquiry.id,
        "inquiry",
    )
    db.commit()
    return (
        db.query(InquiryMessages)
        .options(selectinload(InquiryMessages.sender))
        .filter(InquiryMessages.id == message.id)
        .first()
    )


def list_purchases(
    db: Session,
    buyer: User,
    page: int,
    limit: int,
    transaction_status: TransactionStatus | None = None,
):
    ensure_buyer(buyer)
    query = _purchase_query(db).filter(Transactions.buyer_id == buyer.id)
    if transaction_status is not None:
        query = query.filter(Transactions.transaction_status == transaction_status)
    return paginate(query.order_by(Transactions.created_at.desc(), Transactions.id.desc()), page, limit)


def get_purchase(db: Session, transaction_id: int, buyer: User) -> Transactions:
    ensure_buyer(buyer)
    transaction = _purchase_query(db).filter(
        Transactions.id == transaction_id,
        Transactions.buyer_id == buyer.id,
    ).first()
    if not transaction:
        raise LookupError("Purchase transaction not found.")
    return transaction


def get_dashboard(db: Session, buyer: User) -> dict[str, int]:
    ensure_buyer(buyer)
    return {
        "total_favorite_cars": db.query(Favorites).filter(Favorites.user_id == buyer.id).count(),
        "active_inquiries": db.query(Inquiries).filter(
            Inquiries.buyer_id == buyer.id,
            Inquiries.status.in_([InquiryStatus.OPEN, InquiryStatus.CONTACTED]),
        ).count(),
        "recently_viewed_cars": db.query(ListingViews).filter(ListingViews.buyer_id == buyer.id).count(),
        "purchase_history": db.query(Transactions).filter(
            Transactions.buyer_id == buyer.id,
            Transactions.transaction_status == TransactionStatus.COMPLETED,
        ).count(),
    }


def _inquiry_query(db: Session, include_messages: bool = False):
    options = [selectinload(Inquiries.listing), selectinload(Inquiries.seller)]
    if include_messages:
        options.append(selectinload(Inquiries.messages).selectinload(InquiryMessages.sender))
    return db.query(Inquiries).options(*options)


def _get_inquiry_participant(db: Session, inquiry_id: int, user: User) -> Inquiries:
    inquiry = _inquiry_query(db, include_messages=True).filter(Inquiries.id == inquiry_id).first()
    if not inquiry:
        raise LookupError("Inquiry not found.")
    if user.id not in {inquiry.buyer_id, inquiry.seller_id}:
        raise PermissionError("You are not a participant in this inquiry.")
    return inquiry


def _purchase_query(db: Session):
    return db.query(Transactions).options(
        selectinload(Transactions.listing),
        selectinload(Transactions.seller),
    )


def _listing_detail_loads(relationship):
    return (
        selectinload(relationship)
        .selectinload(Listings.car)
        .selectinload(Cars.variant)
        .selectinload(CarVariants.model)
        .selectinload(CarModels.brand),
        selectinload(relationship).selectinload(Listings.car).selectinload(Cars.media),
        selectinload(relationship).selectinload(Listings.car).selectinload(Cars.features),
    )

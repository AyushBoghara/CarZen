from sqlalchemy.orm import Session, selectinload

from app.models.enums.UserRoles import UserRoles
from app.models.enums.OrderEnums import NotificationType
from app.models.inquiries import Inquiries, InquiryStatus
from app.models.inquiry_messages import InquiryMessages
from app.models.users import User
from app.services.car.catalog_service import paginate
from app.services.notifications import notification_service


# SELLER_ROLES = {UserRoles.SELLER, UserRoles.RESELLER}
SELLER_ROLES = {UserRoles.SELLER}

def ensure_seller(user: User) -> None:
    if user.role not in SELLER_ROLES:
        raise PermissionError("Seller or reseller access required.")


def list_seller_inquiries(
    db: Session,
    seller: User,
    page: int,
    limit: int,
    inquiry_status: InquiryStatus | None = None,
):
    ensure_seller(seller)
    query = _inquiry_query(db).filter(Inquiries.seller_id == seller.id)
    if inquiry_status is not None:
        query = query.filter(Inquiries.status == inquiry_status)
    return paginate(query.order_by(Inquiries.updated_at.desc(), Inquiries.id.desc()), page, limit)


def get_seller_inquiry(db: Session, inquiry_id: int, seller: User) -> Inquiries:
    ensure_seller(seller)
    inquiry = _inquiry_query(db, include_messages=True).filter(
        Inquiries.id == inquiry_id,
        Inquiries.seller_id == seller.id,
    ).first()
    if not inquiry:
        raise LookupError("Inquiry not found.")
    return inquiry


def update_inquiry_status(
    db: Session,
    inquiry_id: int,
    seller: User,
    inquiry_status: InquiryStatus,
) -> Inquiries:
    inquiry = get_seller_inquiry(db, inquiry_id, seller)
    inquiry.status = inquiry_status
    notification_service.create_notification(
        db,
        inquiry.buyer_id,
        NotificationType.INQUIRY,
        "Inquiry status updated",
        f"Your inquiry is now {inquiry_status.value}.",
        inquiry.id,
        "inquiry",
    )
    db.commit()
    return get_seller_inquiry(db, inquiry_id, seller)


def send_seller_message(
    db: Session,
    inquiry_id: int,
    seller: User,
    values: dict,
) -> InquiryMessages:
    inquiry = get_seller_inquiry(db, inquiry_id, seller)
    message = InquiryMessages(inquiry_id=inquiry.id, sender_id=seller.id, **values)
    if inquiry.status == InquiryStatus.OPEN:
        inquiry.status = InquiryStatus.CONTACTED
    db.add(message)
    notification_service.create_notification(
        db,
        inquiry.buyer_id,
        NotificationType.INQUIRY,
        "Seller replied to your inquiry",
        f"The seller replied about {inquiry.listing.title}.",
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


def _inquiry_query(db: Session, include_messages: bool = False):
    options = [selectinload(Inquiries.listing), selectinload(Inquiries.buyer)]
    if include_messages:
        options.append(selectinload(Inquiries.messages).selectinload(InquiryMessages.sender))
    return db.query(Inquiries).options(*options)

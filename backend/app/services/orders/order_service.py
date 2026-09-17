from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload

from app.models.car_models import CarModels
from app.models.car_variants import CarVariants
from app.models.cars import Cars
from app.models.enums.CarEnums import CarApprovalStatus
from app.models.enums.ListingEnums import ListingStatus
from app.models.enums.OrderEnums import NotificationType, OrderStatus
from app.models.enums.UserRoles import UserRoles
from app.models.listings import Listings
from app.models.orders import Orders
from app.models.enums.TransactionEnums import PaymentStatus
from app.models.users import User
from app.services.car.catalog_service import paginate
from app.services.notifications import notification_service


BUYER_ROLES = {UserRoles.USER}
# SELLER_ROLES = {UserRoles.SELLER, UserRoles.RESELLER}
SELLER_ROLES = {UserRoles.SELLER}
ACTIVE_ORDER_STATUSES = {OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING}


def create_order(db: Session, listing_id: int, buyer: User, values: dict) -> Orders:
    _ensure_buyer(buyer)
    
    listing = _get_active_listing(db, listing_id)
    
    if listing.seller_id == buyer.id:
        raise ValueError("You cannot create an order for your own listing.")
    if db.query(Orders).filter(
        Orders.listing_id == listing.id,
        Orders.buyer_id == buyer.id,
        Orders.status.in_(ACTIVE_ORDER_STATUSES),
    ).first():
        raise ValueError("You already have an active order for this listing.")

    order = Orders(
        listing_id=listing.id,
        car_id=listing.car_id,
        buyer_id=buyer.id,
        seller_id=listing.seller_id,
        **values,
    )
    
    db.add(order)
    db.flush()
    
    notification_service.create_notification(
        db,
        listing.seller_id,
        NotificationType.ORDER,
        "New order received",
        f"A buyer placed an order for {listing.title}.",
        order.id,
        "order",
    )
    notification_service.create_notification(
        db,
        buyer.id,
        NotificationType.ORDER,
        "Order created",
        f"Your order for {listing.title} is pending seller confirmation.",
        order.id,
        "order",
    )
    db.commit()
    return get_order_for_user(db, order.id, buyer)


def get_order_for_user(db: Session, order_id: int, user: User) -> Orders:
    order = _order_query(db).filter(Orders.id == order_id).first()
    if not order:
        raise LookupError("Order not found.")
    if user.role != UserRoles.ADMIN and user.id not in {order.buyer_id, order.seller_id}:
        raise PermissionError("You do not have access to this order.")
    return order


def list_buyer_orders(db: Session, buyer: User, page: int, limit: int, order_status: OrderStatus | None = None):
    _ensure_buyer(buyer)
    query = _order_query(db).filter(Orders.buyer_id == buyer.id)
    if order_status is not None:
        query = query.filter(Orders.status == order_status)
    return paginate(query.order_by(Orders.created_at.desc(), Orders.id.desc()), page, limit)


def cancel_buyer_order(db: Session, order_id: int, buyer: User) -> Orders:
    _ensure_buyer(buyer)
    order = get_order_for_user(db, order_id, buyer)
    if order.buyer_id != buyer.id:
        raise PermissionError("You do not own this order.")
    _change_status(db, order, OrderStatus.CANCELLED)
    notification_service.create_notification(
        db,
        order.seller_id,
        NotificationType.ORDER,
        "Order cancelled by buyer",
        f"The buyer cancelled the order for {order.listing.title}.",
        order.id,
        "order",
    )
    db.commit()
    return get_order_for_user(db, order.id, buyer)


def list_seller_orders(db: Session, seller: User, page: int, limit: int, order_status: OrderStatus | None = None):
    _ensure_seller(seller)
    query = _order_query(db).filter(Orders.seller_id == seller.id)
    if order_status is not None:
        query = query.filter(Orders.status == order_status)
    return paginate(query.order_by(Orders.created_at.desc(), Orders.id.desc()), page, limit)


def accept_order(db: Session, order_id: int, seller: User) -> Orders:
    order = _get_seller_order(db, order_id, seller)
    if order.status != OrderStatus.PENDING:
        raise ValueError("Only pending orders can be accepted.")
    if db.query(Orders).filter(
        Orders.listing_id == order.listing_id,
        Orders.id != order.id,
        Orders.status.in_([OrderStatus.CONFIRMED, OrderStatus.PROCESSING]),
    ).first():
        raise ValueError("This listing already has a confirmed order.")
    _change_status(db, order, OrderStatus.CONFIRMED)
    order.listing.listing_status = ListingStatus.RESERVED
    notification_service.create_notification(
        db, order.buyer_id, NotificationType.ORDER, "Order confirmed",
        f"The seller confirmed your order for {order.listing.title}.", order.id, "order",
    )
    db.commit()
    return get_order_for_user(db, order.id, seller)


def reject_order(db: Session, order_id: int, seller: User) -> Orders:
    order = _get_seller_order(db, order_id, seller)
    _change_status(db, order, OrderStatus.REJECTED)
    notification_service.create_notification(
        db, order.buyer_id, NotificationType.ORDER, "Order rejected",
        f"The seller rejected your order for {order.listing.title}.", order.id, "order",
    )
    db.commit()
    return get_order_for_user(db, order.id, seller)


def update_seller_order_status(db: Session, order_id: int, seller: User, target: OrderStatus) -> Orders:
    order = _get_seller_order(db, order_id, seller)
    
    if target not in {OrderStatus.PROCESSING, OrderStatus.COMPLETED}:
        raise ValueError("Sellers can update orders only to processing or completed.")
    
    _change_status(db, order, target)
    
    notification_service.create_notification(
        db, order.buyer_id, NotificationType.ORDER, f"Order {target.value}",
        f"Your order for {order.listing.title} is now {target.value}.", order.id, "order",
    )
    db.commit()
    return get_order_for_user(db, order.id, seller)


def list_admin_orders(db: Session, page: int, limit: int, order_status: OrderStatus | None = None):
    query = _order_query(db)
    if order_status is not None:
        query = query.filter(Orders.status == order_status)
    return paginate(query.order_by(Orders.created_at.desc(), Orders.id.desc()), page, limit)


def update_admin_order_status(db: Session, order_id: int, admin: User, target: OrderStatus) -> Orders:
    order = get_order_for_user(db, order_id, admin)
    if target == OrderStatus.CANCELLED and order.status not in {OrderStatus.CANCELLED, OrderStatus.COMPLETED, OrderStatus.REJECTED}:
        _cancel_order(db, order)
    else:
        _change_status(db, order, target)
    notification_service.create_notification(
        db, order.buyer_id, NotificationType.ADMIN, "Order updated by admin",
        f"An administrator changed your order for {order.listing.title} to {target.value}.", order.id, "order",
    )
    notification_service.create_notification(
        db, order.seller_id, NotificationType.ADMIN, "Order updated by admin",
        f"An administrator changed the order for {order.listing.title} to {target.value}.", order.id, "order",
    )
    db.commit()
    return get_order_for_user(db, order.id, admin)


def _get_active_listing(db: Session, listing_id: int) -> Listings:
    listing = _listing_query(db).filter(
        Listings.id == listing_id,
        Listings.deleted_at.is_(None),
        Listings.listing_status == ListingStatus.ACTIVE,
    ).first()
    if not listing:
        raise LookupError("Active listing not found.")
    return listing


def _get_seller_order(db: Session, order_id: int, seller: User) -> Orders:
    _ensure_seller(seller)
    order = get_order_for_user(db, order_id, seller)
    if order.seller_id != seller.id:
        raise PermissionError("You do not own this order.")
    return order


def _change_status(db: Session, order: Orders, target: OrderStatus) -> None:
    allowed = {
        OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED, OrderStatus.REJECTED},
        OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
        OrderStatus.PROCESSING: {OrderStatus.COMPLETED},
    }
    if target not in allowed.get(order.status, set()):
        raise ValueError(f"Cannot change an order from {order.status.value} to {target.value}.")
    if target == OrderStatus.CANCELLED:
        _cancel_order(db, order)
        return
    if target == OrderStatus.COMPLETED and order.payment_status != PaymentStatus.PAID:
        raise ValueError("An order can be completed only after payment is confirmed.")
    order.status = target
    if target == OrderStatus.COMPLETED:
        order.completed_at = datetime.now(timezone.utc)
        order.listing.listing_status = ListingStatus.SOLD
        order.car.approval_status = CarApprovalStatus.SOLD
        notification_service.notify_favorite_users(
            db,
            order.car_id,
            NotificationType.FAVORITE,
            "Favorite car sold",
            f"{order.listing.title} has been sold.",
            order.id,
            "order",
        )


def _cancel_order(db: Session, order: Orders) -> None:
    order.status = OrderStatus.CANCELLED
    has_reserved_order = db.query(Orders).filter(
        Orders.listing_id == order.listing_id,
        Orders.id != order.id,
        Orders.status.in_([OrderStatus.CONFIRMED, OrderStatus.PROCESSING]),
    ).first()
    if order.listing.listing_status == ListingStatus.RESERVED and not has_reserved_order:
        order.listing.listing_status = ListingStatus.ACTIVE


def _ensure_buyer(user: User) -> None:
    if user.role not in BUYER_ROLES:
        raise PermissionError("Buyer or user access required.")


def _ensure_seller(user: User) -> None:
    if user.role not in SELLER_ROLES:
        raise PermissionError("Seller or reseller access required.")


def _listing_query(db: Session):
    return db.query(Listings).options(selectinload(Listings.car))


def _order_query(db: Session):
    return db.query(Orders).options(
        selectinload(Orders.buyer),
        selectinload(Orders.seller),
        selectinload(Orders.listing),
        selectinload(Orders.car)
        .selectinload(Cars.variant)
        .selectinload(CarVariants.model)
        .selectinload(CarModels.brand),
        selectinload(Orders.car).selectinload(Cars.media),
        selectinload(Orders.car).selectinload(Cars.features),
    )

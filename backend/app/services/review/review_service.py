from datetime import datetime
from sqlalchemy.orm import Session, selectinload

from app.models.enums.TransactionEnums import TransactionStatus
from app.models.enums.UserRoles import UserRoles
from app.models.reviews import Reviews
from app.models.transactions import Transactions
from app.models.users import User
from app.services.car.catalog_service import paginate


def create_review(db: Session, user: User, data: dict) -> Reviews:
    car_id = data["car_id"]
    rating = data["rating"]
    transaction_id = data.get("transaction_id")

    # 1. Rating validation
    if not (1 <= rating <= 5):
        raise ValueError("Rating must be an integer between 1 and 5.")

    # 2. Purchase verification
    # User must have a completed transaction for this car as buyer
    txn_query = db.query(Transactions).filter(
        Transactions.car_id == car_id,
        Transactions.buyer_id == user.id,
        Transactions.transaction_status == TransactionStatus.COMPLETED,
    )

    if transaction_id:
        txn = txn_query.filter(Transactions.id == transaction_id).first()
        if not txn:
            raise PermissionError("You cannot review a purchase that does not belong to you or is not completed.")
    else:
        txn = txn_query.first()
        if not txn:
            raise PermissionError("Only buyers who completed a purchase of this car can leave a review.")
        transaction_id = txn.id

    # 3. Duplicate review prevention
    existing = (
        db.query(Reviews)
        .filter(
            Reviews.user_id == user.id,
            Reviews.car_id == car_id,
            Reviews.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        raise ValueError("You have already submitted a review for this purchase.")

    review = Reviews(
        user_id=user.id,
        car_id=car_id,
        listing_id=txn.listing_id,
        transaction_id=transaction_id,
        rating=rating,
        title=data.get("title"),
        review_text=data.get("review_text"),
        is_visible=True,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def list_my_reviews(db: Session, user: User, page: int = 1, limit: int = 20):
    query = (
        db.query(Reviews)
        .options(
            selectinload(Reviews.user),
            selectinload(Reviews.car),
        )
        .filter(
            Reviews.user_id == user.id,
            Reviews.deleted_at.is_(None),
        )
    )
    return paginate(query.order_by(Reviews.created_at.desc(), Reviews.id.desc()), page, limit)


def list_car_reviews(db: Session, car_id: int, page: int = 1, limit: int = 20):
    query = (
        db.query(Reviews)
        .options(
            selectinload(Reviews.user),
            selectinload(Reviews.car),
        )
        .filter(
            Reviews.car_id == car_id,
            Reviews.is_visible.is_(True),
            Reviews.deleted_at.is_(None),
        )
    )
    return paginate(query.order_by(Reviews.created_at.desc(), Reviews.id.desc()), page, limit)


def update_own_review(db: Session, review_id: int, user: User, values: dict) -> Reviews:
    review = (
        db.query(Reviews)
        .filter(Reviews.id == review_id, Reviews.deleted_at.is_(None))
        .first()
    )
    if not review:
        raise LookupError("Review not found.")

    if review.user_id != user.id and user.role != UserRoles.ADMIN:
        raise PermissionError("You can only edit your own review.")

    if "rating" in values and values["rating"] is not None:
        if not (1 <= values["rating"] <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        review.rating = values["rating"]

    if "title" in values:
        review.title = values["title"]

    if "review_text" in values:
        review.review_text = values["review_text"]

    review.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(review)
    return review


def delete_own_review(db: Session, review_id: int, user: User) -> None:
    review = (
        db.query(Reviews)
        .filter(Reviews.id == review_id, Reviews.deleted_at.is_(None))
        .first()
    )
    if not review:
        raise LookupError("Review not found.")

    if review.user_id != user.id and user.role != UserRoles.ADMIN:
        raise PermissionError("You can only delete your own review.")

    review.deleted_at = datetime.utcnow()
    db.commit()


# --- Admin APIs ---

def list_admin_reviews(
    db: Session,
    page: int = 1,
    limit: int = 20,
    is_visible: bool | None = None,
    car_id: int | None = None,
):
    query = (
        db.query(Reviews)
        .options(
            selectinload(Reviews.user),
            selectinload(Reviews.car),
        )
        .filter(Reviews.deleted_at.is_(None))
    )
    if is_visible is not None:
        query = query.filter(Reviews.is_visible == is_visible)
    if car_id:
        query = query.filter(Reviews.car_id == car_id)

    return paginate(query.order_by(Reviews.created_at.desc(), Reviews.id.desc()), page, limit)


def set_review_visibility(db: Session, review_id: int, is_visible: bool) -> Reviews:
    review = (
        db.query(Reviews)
        .options(
            selectinload(Reviews.user),
            selectinload(Reviews.car),
        )
        .filter(Reviews.id == review_id, Reviews.deleted_at.is_(None))
        .first()
    )
    if not review:
        raise LookupError("Review not found.")

    review.is_visible = is_visible
    review.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(review)
    return review


def admin_delete_review(db: Session, review_id: int) -> None:
    review = (
        db.query(Reviews)
        .filter(Reviews.id == review_id, Reviews.deleted_at.is_(None))
        .first()
    )
    if not review:
        raise LookupError("Review not found.")

    review.deleted_at = datetime.utcnow()
    db.commit()

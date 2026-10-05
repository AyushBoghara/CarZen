from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.enums.TransactionEnums import TransactionStatus
from app.models.enums.UserRoles import UserRoles
from app.models.transactions import Transactions
from app.models.users import User
from app.services.car.catalog_service import paginate


def _base_query(db: Session):
    return db.query(Transactions).options(
        selectinload(Transactions.buyer),
        selectinload(Transactions.seller),
        selectinload(Transactions.car),
        selectinload(Transactions.listing),
    )


def list_user_transactions(
    db: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    status: TransactionStatus | None = None,
):
    query = _base_query(db).filter(
        or_(
            Transactions.buyer_id == user.id,
            Transactions.seller_id == user.id,
        )
    )
    if status:
        query = query.filter(Transactions.transaction_status == status)

    return paginate(
        query.order_by(Transactions.created_at.desc(), Transactions.id.desc()),
        page,
        limit,
    )


def get_user_transaction(db: Session, transaction_id: int, user: User) -> Transactions:
    transaction = _base_query(db).filter(Transactions.id == transaction_id).first()
    if not transaction:
        raise LookupError("Transaction not found.")

    if (
        transaction.buyer_id != user.id
        and transaction.seller_id != user.id
        and user.role != UserRoles.ADMIN
    ):
        raise PermissionError("You do not have permission to view this transaction.")

    return transaction


def list_buyer_transactions(
    db: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    status: TransactionStatus | None = None,
):
    query = _base_query(db).filter(Transactions.buyer_id == user.id)
    if status:
        query = query.filter(Transactions.transaction_status == status)

    return paginate(
        query.order_by(Transactions.created_at.desc(), Transactions.id.desc()),
        page,
        limit,
    )


def list_seller_transactions(
    db: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    status: TransactionStatus | None = None,
):
    query = _base_query(db).filter(Transactions.seller_id == user.id)
    if status:
        query = query.filter(Transactions.transaction_status == status)

    return paginate(
        query.order_by(Transactions.created_at.desc(), Transactions.id.desc()),
        page,
        limit,
    )


# --- Admin APIs ---

def list_admin_transactions(
    db: Session,
    page: int = 1,
    limit: int = 20,
    buyer_id: int | None = None,
    seller_id: int | None = None,
    status: TransactionStatus | None = None,
):
    query = _base_query(db)
    if buyer_id:
        query = query.filter(Transactions.buyer_id == buyer_id)
    if seller_id:
        query = query.filter(Transactions.seller_id == seller_id)
    if status:
        query = query.filter(Transactions.transaction_status == status)

    return paginate(
        query.order_by(Transactions.created_at.desc(), Transactions.id.desc()),
        page,
        limit,
    )


def get_admin_transaction(db: Session, transaction_id: int) -> Transactions:
    transaction = _base_query(db).filter(Transactions.id == transaction_id).first()
    if not transaction:
        raise LookupError("Transaction not found.")
    return transaction

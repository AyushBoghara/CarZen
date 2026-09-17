from alembic import op
import sqlalchemy as sa


revision = "20260917_01"
down_revision = None
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _columns(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    # The conditional checks keep the revision safe for installations where
    # create_all() created these tables before Alembic was introduced.
    if not _table_exists("payments"):
        op.create_table(
            "payments",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("transaction_id", sa.BigInteger(), sa.ForeignKey("transactions.id"), nullable=True),
            sa.Column("order_id", sa.BigInteger(), sa.ForeignKey("orders.id"), nullable=True),
            sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("amount", sa.Numeric(15, 2), nullable=False),
            sa.Column("currency", sa.String(10), nullable=False, server_default="INR"),
            sa.Column("payment_method", sa.Enum("CASH", "UPI", "CARD", "BANK_TRANSFER", "FINANCE", "OTHER", name="paymentmethod"), nullable=True),
            sa.Column("provider", sa.String(100), nullable=True),
            sa.Column("provider_transaction_id", sa.String(255), nullable=True),
            sa.Column("status", sa.Enum("pending", "processing", "success", "failed", "cancelled", "refunded", name="gatewaypaymentstatus"), nullable=False, server_default="pending"),
            sa.Column("razorpay_order_id", sa.String(255), nullable=True, unique=True),
            sa.Column("razorpay_payment_id", sa.String(255), nullable=True, unique=True),
            sa.Column("razorpay_signature", sa.String(512), nullable=True),
            sa.Column("payment_date", sa.DateTime(), nullable=True),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )

    if _table_exists("payments"):
        columns = _columns("payments")
        missing_columns = {
            "order_id": sa.Column("order_id", sa.BigInteger(), sa.ForeignKey("orders.id"), nullable=True),
            "user_id": sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
            "razorpay_order_id": sa.Column("razorpay_order_id", sa.String(255), nullable=True),
            "razorpay_payment_id": sa.Column("razorpay_payment_id", sa.String(255), nullable=True),
            "razorpay_signature": sa.Column("razorpay_signature", sa.String(512), nullable=True),
        }
        for name, column in missing_columns.items():
            if name not in columns:
                op.add_column("payments", column)

        indexes = _indexes("payments")
        if "ix_payments_order_id" not in indexes:
            op.create_index("ix_payments_order_id", "payments", ["order_id"])
        if "ix_payments_user_id" not in indexes:
            op.create_index("ix_payments_user_id", "payments", ["user_id"])
        if "ix_payments_razorpay_order_id" not in indexes:
            op.create_index("ix_payments_razorpay_order_id", "payments", ["razorpay_order_id"], unique=True)
        if "ix_payments_razorpay_payment_id" not in indexes:
            op.create_index("ix_payments_razorpay_payment_id", "payments", ["razorpay_payment_id"], unique=True)

    if _table_exists("reports"):
        columns = _columns("reports")
        if "resolved_by_id" not in columns:
            op.add_column("reports", sa.Column("resolved_by_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True))
        if "admin_note" not in columns:
            op.add_column("reports", sa.Column("admin_note", sa.Text(), nullable=True))
        indexes = _indexes("reports")
        for name, column in (
            ("ix_reports_reporter_id", "reporter_id"),
            ("ix_reports_listing_id", "listing_id"),
            ("ix_reports_car_id", "car_id"),
        ):
            if name not in indexes:
                op.create_index(name, "reports", [column])


def downgrade() -> None:
    if _table_exists("reports"):
        indexes = _indexes("reports")
        for name in ("ix_reports_car_id", "ix_reports_listing_id", "ix_reports_reporter_id"):
            if name in indexes:
                op.drop_index(name, table_name="reports")
        columns = _columns("reports")
        if "admin_note" in columns:
            op.drop_column("reports", "admin_note")
        if "resolved_by_id" in columns:
            op.drop_column("reports", "resolved_by_id")
    if _table_exists("payments"):
        indexes = _indexes("payments")
        for name in (
            "ix_payments_razorpay_payment_id",
            "ix_payments_razorpay_order_id",
            "ix_payments_user_id",
            "ix_payments_order_id",
        ):
            if name in indexes:
                op.drop_index(name, table_name="payments")
        columns = _columns("payments")
        for name in (
            "razorpay_signature",
            "razorpay_payment_id",
            "razorpay_order_id",
            "user_id",
            "order_id",
        ):
            if name in columns:
                op.drop_column("payments", name)

from alembic import op
import sqlalchemy as sa


revision = "20260922_03"
down_revision = "20260921_02"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _columns(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    # 1. Create service_bookings table
    if not _table_exists("service_bookings"):
        op.create_table(
            "service_bookings",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("car_id", sa.BigInteger(), sa.ForeignKey("cars.id"), nullable=False),
            sa.Column("service_center_id", sa.BigInteger(), sa.ForeignKey("service_centers.id") if _table_exists("service_centers") else None, nullable=False),
            sa.Column("service_type", sa.String(150), nullable=False),
            sa.Column("booking_date", sa.Date(), nullable=False),
            sa.Column("booking_time", sa.Time(), nullable=False),
            sa.Column("problem_description", sa.Text(), nullable=True),
            sa.Column("estimated_cost", sa.Numeric(15, 2), nullable=True),
            sa.Column(
                "status",
                sa.Enum(
                    "pending",
                    "confirmed",
                    "in_progress",
                    "completed",
                    "cancelled",
                    "rejected",
                    name="servicebookingstatus",
                ),
                nullable=False,
                server_default="pending",
            ),
            sa.Column("cancellation_reason", sa.Text(), nullable=True),
            sa.Column("service_record_id", sa.BigInteger(), sa.ForeignKey("service_records.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
        )

        for col in ("id", "user_id", "car_id", "service_center_id", "booking_date", "status", "service_record_id"):
            idx_name = f"ix_service_bookings_{col}"
            op.create_index(idx_name, "service_bookings", [col])

    # 2. Add transaction_id to reviews
    if _table_exists("reviews"):
        columns = _columns("reviews")
        if "transaction_id" not in columns:
            op.add_column(
                "reviews",
                sa.Column("transaction_id", sa.BigInteger(), sa.ForeignKey("transactions.id"), nullable=True),
            )
        indexes = _indexes("reviews")
        if "ix_reviews_transaction_id" not in indexes:
            op.create_index("ix_reviews_transaction_id", "reviews", ["transaction_id"])

    # 3. Update listings.listing_status enum in MySQL
    if _table_exists("listings") and dialect_name == "mysql":
        try:
            op.execute(
                "ALTER TABLE listings MODIFY COLUMN listing_status "
                "ENUM('DRAFT', 'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'ACTIVE', 'RESERVED', 'SOLD', 'EXPIRED', 'CANCELLED', 'REMOVED', 'SUSPENDED') "
                "DEFAULT 'DRAFT'"
            )
        except Exception:
            pass


def downgrade() -> None:
    if _table_exists("reviews"):
        indexes = _indexes("reviews")
        if "ix_reviews_transaction_id" in indexes:
            op.drop_index("ix_reviews_transaction_id", table_name="reviews")
        columns = _columns("reviews")
        if "transaction_id" in columns:
            op.drop_column("reviews", "transaction_id")

    if _table_exists("service_bookings"):
        op.drop_table("service_bookings")

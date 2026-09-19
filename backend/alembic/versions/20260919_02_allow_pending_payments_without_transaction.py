"""Allow gateway payment attempts before a transaction exists.

Revision ID: 20260919_02
Revises: 20260917_02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260919_02"
down_revision = "20260917_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # A Razorpay order is created before its payment has been captured, so it
    # cannot yet be associated with a completed Transactions record.
    op.alter_column(
        "payments",
        "transaction_id",
        existing_type=sa.BigInteger(),
        nullable=True,
    )

    # Older installations used the order-level PaymentStatus enum (uppercase
    # PENDING/PAID/etc.).  Gateway payment attempts use the lowercase values
    # in GatewayPaymentStatus, so migrate existing values before enforcing the
    # new enum.  A VARCHAR intermediary avoids case-insensitive duplicate enum
    # members such as PENDING and pending on MySQL.
    desired_values = ("pending", "processing", "success", "failed", "cancelled", "refunded")
    status_column = next(
        column
        for column in sa.inspect(op.get_bind()).get_columns("payments")
        if column["name"] == "status"
    )
    current_values = tuple(getattr(status_column["type"], "enums", ()))
    if current_values != desired_values:
        op.execute("ALTER TABLE payments MODIFY status VARCHAR(20) NULL")
        op.execute(
            """
            UPDATE payments
            SET status = CASE status
                WHEN 'PENDING' THEN 'pending'
                WHEN 'PARTIAL' THEN 'processing'
                WHEN 'PAID' THEN 'success'
                WHEN 'FAILED' THEN 'failed'
                WHEN 'REFUNDED' THEN 'refunded'
                ELSE COALESCE(status, 'pending')
            END
            """
        )
        final_values = ", ".join(f"'{value}'" for value in desired_values)
        op.execute(
            f"ALTER TABLE payments MODIFY status ENUM({final_values}) NOT NULL DEFAULT 'pending'"
        )


def downgrade() -> None:
    op.alter_column(
        "payments",
        "transaction_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )

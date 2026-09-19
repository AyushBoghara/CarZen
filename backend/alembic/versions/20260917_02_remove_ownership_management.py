"""Remove the retired ownership-history table.

Revision ID: 20260917_02
Revises: 20260917_01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260917_02"
down_revision = "20260917_01"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _table_exists("ownership_history"):
        op.drop_table("ownership_history")


def downgrade() -> None:
    if not _table_exists("ownership_history"):
        op.create_table(
            "ownership_history",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("car_id", sa.BigInteger(), sa.ForeignKey("cars.id"), nullable=False),
            sa.Column("owner_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("ownership_number", sa.Integer(), nullable=False),
            sa.Column("ownership_type", sa.Enum("first_owner", "second_owner", "third_owner", "fourth_or_more", name="ownershiptype"), nullable=True),
            sa.Column("purchase_date", sa.Date(), nullable=True),
            sa.Column("sale_date", sa.Date(), nullable=True),
            sa.Column("purchase_price", sa.Numeric(15, 2), nullable=True),
            sa.Column("sale_price", sa.Numeric(15, 2), nullable=True),
            sa.Column("purchase_location", sa.String(150), nullable=True),
            sa.Column("sale_location", sa.String(150), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )

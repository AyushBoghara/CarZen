"""create service_request_items table for multi-service support

Revision ID: 20260922_07
Revises: 20260922_06
Create Date: 2026-09-22 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '20260922_07'
down_revision = '20260922_06'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = set(inspector.get_table_names())

    # 1. Create service_request_items table
    if 'service_request_items' not in tables:
        op.create_table(
            'service_request_items',
            sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True, index=True),
            sa.Column(
                'service_request_id',
                sa.BigInteger(),
                sa.ForeignKey('service_requests.id', ondelete='CASCADE'),
                nullable=False,
            ),
            sa.Column(
                'service_id',
                sa.BigInteger(),
                sa.ForeignKey('services.id', ondelete='SET NULL'),
                nullable=True,
            ),
            sa.Column('service_name', sa.String(length=150), nullable=False),
            sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('duration_minutes', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
        op.create_index(
            'ix_service_request_items_service_request_id',
            'service_request_items',
            ['service_request_id'],
        )
        op.create_index(
            'ix_service_request_items_service_id',
            'service_request_items',
            ['service_id'],
        )

    # 2. Make service_requests.service_id nullable for pure multi-item orders
    if 'service_requests' in tables:
        op.alter_column(
            'service_requests',
            'service_id',
            existing_type=sa.BigInteger(),
            nullable=True,
        )


def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = set(inspector.get_table_names())

    if 'service_request_items' in tables:
        op.drop_table('service_request_items')

    if 'service_requests' in tables:
        op.alter_column(
            'service_requests',
            'service_id',
            existing_type=sa.BigInteger(),
            nullable=False,
        )

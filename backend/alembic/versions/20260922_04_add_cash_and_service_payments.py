"""add cash and service payments

Revision ID: 20260922_04
Revises: 20260922_03
Create Date: 2026-09-22 18:16:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '20260922_04'
down_revision = '20260922_03'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    # 1. Update payments table: add service_booking_id
    payments_cols = {c['name'] for c in inspector.get_columns('payments')}
    if 'service_booking_id' not in payments_cols:
        op.add_column(
            'payments',
            sa.Column('service_booking_id', sa.BigInteger(), nullable=True)
        )
        op.create_index(
            'ix_payments_service_booking_id',
            'payments',
            ['service_booking_id']
        )
        op.create_foreign_key(
            'fk_payments_service_booking_id',
            'payments',
            'service_bookings',
            ['service_booking_id'],
            ['id']
        )

    # 2. Update service_bookings table: add payment tracking columns
    booking_cols = {c['name'] for c in inspector.get_columns('service_bookings')}
    if 'payment_method' not in booking_cols:
        op.add_column(
            'service_bookings',
            sa.Column('payment_method', sa.String(length=50), nullable=True)
        )

    if 'payment_status' not in booking_cols:
        op.add_column(
            'service_bookings',
            sa.Column('payment_status', sa.String(length=50), server_default='pending', nullable=False)
        )
        op.create_index(
            'ix_service_bookings_payment_status',
            'service_bookings',
            ['payment_status']
        )

    if 'final_amount_paid' not in booking_cols:
        op.add_column(
            'service_bookings',
            sa.Column('final_amount_paid', sa.Numeric(precision=15, scale=2), nullable=True)
        )

    if 'paid_at' not in booking_cols:
        op.add_column(
            'service_bookings',
            sa.Column('paid_at', sa.DateTime(), nullable=True)
        )


def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    # Rollback service_bookings columns
    booking_cols = {c['name'] for c in inspector.get_columns('service_bookings')}
    if 'paid_at' in booking_cols:
        op.drop_column('service_bookings', 'paid_at')
    if 'final_amount_paid' in booking_cols:
        op.drop_column('service_bookings', 'final_amount_paid')
    if 'payment_status' in booking_cols:
        op.drop_index('ix_service_bookings_payment_status', table_name='service_bookings')
        op.drop_column('service_bookings', 'payment_status')
    if 'payment_method' in booking_cols:
        op.drop_column('service_bookings', 'payment_method')

    # Rollback payments table columns
    payments_cols = {c['name'] for c in inspector.get_columns('payments')}
    if 'service_booking_id' in payments_cols:
        op.drop_constraint('fk_payments_service_booking_id', 'payments', type_='foreignkey')
        op.drop_index('ix_payments_service_booking_id', table_name='payments')
        op.drop_column('payments', 'service_booking_id')

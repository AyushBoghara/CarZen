"""remove legacy service_bookings table and foreign keys

Revision ID: 20260922_06
Revises: 20260922_05
Create Date: 2026-09-22 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '20260922_06'
down_revision = '20260922_05'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = set(inspector.get_table_names())

    # 1. Drop foreign key and column on payments if present
    if 'payments' in tables:
        payments_fks = {fk['name'] for fk in inspector.get_foreign_keys('payments')}
        if 'fk_payments_service_booking_id' in payments_fks:
            op.drop_constraint('fk_payments_service_booking_id', 'payments', type_='foreignkey')

        payments_indexes = {idx['name'] for idx in inspector.get_indexes('payments')}
        if 'ix_payments_service_booking_id' in payments_indexes:
            op.drop_index('ix_payments_service_booking_id', table_name='payments')

        payments_cols = {c['name'] for c in inspector.get_columns('payments')}
        if 'service_booking_id' in payments_cols:
            op.drop_column('payments', 'service_booking_id')

    # 2. Drop service_bookings table
    if 'service_bookings' in tables:
        op.drop_table('service_bookings')


def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = set(inspector.get_table_names())

    # 1. Re-create service_bookings table
    if 'service_bookings' not in tables:
        op.create_table(
            'service_bookings',
            sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True, index=True),
            sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('car_id', sa.BigInteger(), sa.ForeignKey('cars.id'), nullable=False),
            sa.Column('service_center_id', sa.BigInteger(), sa.ForeignKey('service_centers.id'), nullable=False),
            sa.Column('service_type', sa.String(length=150), nullable=False),
            sa.Column('booking_date', sa.Date(), nullable=False),
            sa.Column('booking_time', sa.Time(), nullable=False),
            sa.Column('problem_description', sa.Text(), nullable=True),
            sa.Column('estimated_cost', sa.Numeric(precision=15, scale=2), nullable=True),
            sa.Column('status', sa.String(length=50), server_default='pending', nullable=False),
            sa.Column('cancellation_reason', sa.Text(), nullable=True),
            sa.Column('service_record_id', sa.BigInteger(), sa.ForeignKey('service_records.id'), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
            sa.Column('payment_method', sa.String(length=50), nullable=True),
            sa.Column('payment_status', sa.String(length=50), server_default='pending', nullable=False),
            sa.Column('final_amount_paid', sa.Numeric(precision=15, scale=2), nullable=True),
            sa.Column('paid_at', sa.DateTime(), nullable=True),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_service_bookings_booking_date', 'service_bookings', ['booking_date'])
        op.create_index('ix_service_bookings_status', 'service_bookings', ['status'])
        op.create_index('ix_service_bookings_payment_status', 'service_bookings', ['payment_status'])

    # 2. Re-add service_booking_id to payments
    if 'payments' in tables:
        payments_cols = {c['name'] for c in inspector.get_columns('payments')}
        if 'service_booking_id' not in payments_cols:
            op.add_column('payments', sa.Column('service_booking_id', sa.BigInteger(), nullable=True))
            op.create_index('ix_payments_service_booking_id', 'payments', ['service_booking_id'])
            op.create_foreign_key(
                'fk_payments_service_booking_id',
                'payments',
                'service_bookings',
                ['service_booking_id'],
                ['id'],
            )

"""admin provided services and service requests

Revision ID: 20260922_05
Revises: 20260922_04
Create Date: 2026-09-22 19:21:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '20260922_05'
down_revision = '20260922_04'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = set(inspector.get_table_names())

    # 1. Create services table
    if 'services' not in tables:
        op.create_table(
            'services',
            sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True, index=True),
            sa.Column('name', sa.String(length=150), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('price', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('duration_minutes', sa.Integer(), nullable=True),
            sa.Column('image_url', sa.String(length=500), nullable=True),
            sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_services_status', 'services', ['status'])
        op.create_index('ix_services_deleted_at', 'services', ['deleted_at'])

    # 2. Create service_requests table
    if 'service_requests' not in tables:
        op.create_table(
            'service_requests',
            sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True, index=True),
            sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('car_id', sa.BigInteger(), sa.ForeignKey('cars.id'), nullable=False),
            sa.Column('service_id', sa.BigInteger(), sa.ForeignKey('services.id'), nullable=False),
            sa.Column('scheduled_date', sa.Date(), nullable=False),
            sa.Column('scheduled_time', sa.Time(), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('payment_status', sa.String(length=50), server_default='unpaid', nullable=False),
            sa.Column('payment_method', sa.String(length=50), nullable=True),
            sa.Column('status', sa.String(length=50), server_default='REQUESTED', nullable=False),
            sa.Column('admin_note', sa.Text(), nullable=True),
            sa.Column('service_record_id', sa.BigInteger(), sa.ForeignKey('service_records.id'), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_service_requests_user_id', 'service_requests', ['user_id'])
        op.create_index('ix_service_requests_car_id', 'service_requests', ['car_id'])
        op.create_index('ix_service_requests_service_id', 'service_requests', ['service_id'])
        op.create_index('ix_service_requests_status', 'service_requests', ['status'])
        op.create_index('ix_service_requests_payment_status', 'service_requests', ['payment_status'])
        op.create_index('ix_service_requests_scheduled_date', 'service_requests', ['scheduled_date'])

    # 3. Add service_request_id to payments table
    payments_cols = {c['name'] for c in inspector.get_columns('payments')}
    if 'service_request_id' not in payments_cols:
        op.add_column(
            'payments',
            sa.Column('service_request_id', sa.BigInteger(), nullable=True)
        )
        op.create_index(
            'ix_payments_service_request_id',
            'payments',
            ['service_request_id']
        )
        op.create_foreign_key(
            'fk_payments_service_request_id',
            'payments',
            'service_requests',
            ['service_request_id'],
            ['id']
        )


def downgrade():
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    payments_cols = {c['name'] for c in inspector.get_columns('payments')}
    if 'service_request_id' in payments_cols:
        op.drop_constraint('fk_payments_service_request_id', 'payments', type_='foreignkey')
        op.drop_index('ix_payments_service_request_id', table_name='payments')
        op.drop_column('payments', 'service_request_id')

    tables = set(inspector.get_table_names())
    if 'service_requests' in tables:
        op.drop_table('service_requests')

    if 'services' in tables:
        op.drop_table('services')

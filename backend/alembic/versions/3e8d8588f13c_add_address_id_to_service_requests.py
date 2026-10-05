"""add_address_id_to_service_requests

Revision ID: 3e8d8588f13c
Revises: 20260922_07
Create Date: 2026-09-27 19:49:37.801409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '3e8d8588f13c'
down_revision: Union[str, Sequence[str], None] = '20260922_07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add address_id column and FK to service_requests table."""
    # Add the address_id column (nullable so existing rows are not affected)
    op.add_column('service_requests', sa.Column('address_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_service_requests_address_id'), 'service_requests', ['address_id'], unique=False)
    op.create_foreign_key('fk_service_requests_address_id', 'service_requests', 'addresses', ['address_id'], ['id'])


def downgrade() -> None:
    """Remove address_id column from service_requests table."""
    op.drop_constraint('fk_service_requests_address_id', 'service_requests', type_='foreignkey')
    op.drop_index(op.f('ix_service_requests_address_id'), table_name='service_requests')
    op.drop_column('service_requests', 'address_id')

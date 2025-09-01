"""Allow NULL values for price_cost_basis column

Revision ID: allow_null_price_cost_basis
Revises: add_position_foreign_key
Create Date: 2025-01-27 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'allow_null_price_cost_basis'
down_revision = 'add_position_foreign_key'
branch_labels = None
depends_on = None


def upgrade():
    # Allow NULL values for price_cost_basis column
    op.alter_column('trades', 'price_cost_basis', nullable=True)


def downgrade():
    # Revert to NOT NULL constraint
    op.alter_column('trades', 'price_cost_basis', nullable=False)

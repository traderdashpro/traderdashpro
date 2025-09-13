"""fix_null_proceeds_before_constraint

Revision ID: 9815b98158f2
Revises: allow_null_price_cost_basis
Create Date: 2025-09-12 21:09:15.900350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9815b98158f2'
down_revision = 'allow_null_price_cost_basis'
branch_labels = None
depends_on = None


def upgrade():
    # Update NULL proceeds values to 0 before applying NOT NULL constraint
    op.execute("UPDATE trades SET proceeds = 0 WHERE proceeds IS NULL")
    
    # Now make proceeds NOT NULL
    op.alter_column('trades', 'proceeds', nullable=False)


def downgrade():
    # Allow NULL values for proceeds column
    op.alter_column('trades', 'proceeds', nullable=True)

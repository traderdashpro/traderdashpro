"""Allow NULL values for proceeds column

Revision ID: allow_null_proceeds
Revises: update_win_loss_constraint
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'allow_null_proceeds'
down_revision = 'update_win_loss_constraint'
branch_labels = None
depends_on = None


def upgrade():
    # Allow NULL values for proceeds column
    op.alter_column('trades', 'proceeds', nullable=True)


def downgrade():
    # Revert to NOT NULL constraint
    op.alter_column('trades', 'proceeds', nullable=False)

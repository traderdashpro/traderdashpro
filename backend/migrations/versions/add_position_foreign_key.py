"""Add foreign key constraint for position_id

Revision ID: add_position_foreign_key
Revises: allow_null_proceeds
Create Date: 2025-01-27 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_position_foreign_key'
down_revision = 'allow_null_proceeds'
branch_labels = None
depends_on = None


def upgrade():
    # Add foreign key constraint for position_id
    op.create_foreign_key(
        'trades_position_id_fkey',
        'trades',
        'positions',
        ['position_id'],
        ['id']
    )


def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('trades_position_id_fkey', 'trades', type_='foreignkey')

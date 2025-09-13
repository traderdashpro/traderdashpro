"""add_transaction_type_column

Revision ID: 5937ccd68c92
Revises: 9815b98158f2
Create Date: 2025-09-12 21:15:50.184680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5937ccd68c92'
down_revision = '9815b98158f2'
branch_labels = None
depends_on = None


def upgrade():
    # Check if transaction_type column exists, if not add it
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('trades')]
    
    if 'transaction_type' not in columns:
        op.add_column('trades', sa.Column('transaction_type', sa.String(20), nullable=True, default='stock'))


def downgrade():
    # Remove transaction_type column from trades table
    op.drop_column('trades', 'transaction_type')

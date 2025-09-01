"""Add position tracking

Revision ID: add_position_tracking
Revises: ec3ab21c0f7e
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_position_tracking'
down_revision = 'ec3ab21c0f7e'
branch_labels = None
depends_on = None


def upgrade():
    # Add position tracking fields to trades table
    op.add_column('trades', sa.Column('status', sa.String(10), nullable=False, server_default='CLOSED'))
    op.add_column('trades', sa.Column('position_id', sa.String(20), nullable=True))
    op.add_column('trades', sa.Column('shares_remaining', sa.Integer(), nullable=True))
    
    # Create positions table
    op.create_table('positions',
        sa.Column('id', sa.String(20), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('symbol', sa.String(10), nullable=False),
        sa.Column('status', sa.String(10), nullable=False, server_default='OPEN'),
        sa.Column('total_shares', sa.Integer(), nullable=False),
        sa.Column('buy_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('buy_date', sa.Date(), nullable=False),
        sa.Column('sell_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('sell_date', sa.Date(), nullable=True),
        sa.Column('pnl', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on positions for faster lookups
    op.create_index('idx_positions_user_symbol_status', 'positions', ['user_id', 'symbol', 'status'])


def downgrade():
    # Drop positions table
    op.drop_index('idx_positions_user_symbol_status', table_name='positions')
    op.drop_table('positions')
    
    # Remove position tracking fields from trades table
    op.drop_column('trades', 'shares_remaining')
    op.drop_column('trades', 'position_id')
    op.drop_column('trades', 'status')

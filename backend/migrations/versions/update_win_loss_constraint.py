"""Update win_loss constraint to allow Pending

Revision ID: update_win_loss_constraint
Revises: add_position_tracking
Create Date: 2025-01-27 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_win_loss_constraint'
down_revision = 'add_position_tracking'
branch_labels = None
depends_on = None


def upgrade():
    # Update existing trades with null win_loss to 'Pending'
    op.execute("UPDATE trades SET win_loss = 'Pending' WHERE win_loss IS NULL")
    
    # Update the win_loss column to allow 'Pending'
    # First, drop the existing check constraint if it exists
    op.execute("ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_win_loss_check")
    
    # Add new check constraint that includes 'Pending'
    op.execute("ALTER TABLE trades ADD CONSTRAINT trades_win_loss_check CHECK (win_loss IN ('Win', 'Loss', 'Pending'))")


def downgrade():
    # Revert to original constraint
    op.execute("ALTER TABLE trades DROP CONSTRAINT IF EXISTS trades_win_loss_check")
    op.execute("ALTER TABLE trades ADD CONSTRAINT trades_win_loss_check CHECK (win_loss IN ('Win', 'Loss'))")
    
    # Update 'Pending' back to NULL (though this might cause issues if column is NOT NULL)
    op.execute("UPDATE trades SET win_loss = 'Loss' WHERE win_loss = 'Pending'")

"""last_sent nullable false

Revision ID: 39931ee666ed
Revises: 979a1be87c60
Create Date: 2025-06-14 22:00:13.188914
"""

from alembic import op
import sqlalchemy as sa
from datetime import date


# revision identifiers, used by Alembic.
revision = '39931ee666ed'
down_revision = '979a1be87c60'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Set a default for NULLs
    op.execute("UPDATE anecdotes SET last_sent = '9999-12-31' WHERE last_sent IS NULL")

    # Step 2: Rebuild table with NOT NULL constraint (required for SQLite)
    with op.batch_alter_table('anecdotes', recreate='always') as batch_op:
        batch_op.alter_column('last_sent',
                              existing_type=sa.Date(),
                              nullable=False)


def downgrade():
    with op.batch_alter_table('anecdotes', recreate='always') as batch_op:
        batch_op.alter_column('last_sent',
                              existing_type=sa.Date(),
                              nullable=True)

"""Your migration message here

Revision ID: 7d26de48ed5d
Revises: cdcb858b2666
Create Date: 2025-06-08 18:30:01.015368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d26de48ed5d'
down_revision: Union[str, None] = 'cdcb858b2666'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('anecdotes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('anecdote', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('anecdotes')
    # ### end Alembic commands ###

"""user avatar and confirm

Revision ID: 51933a5223be
Revises: fee87ceece57
Create Date: 2024-01-26 14:15:04.805838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51933a5223be'
down_revision: Union[str, None] = 'fee87ceece57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatar_cld', sa.String(length=150), nullable=True))
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    op.drop_column('users', 'avatar_cld')
    op.drop_column('users', 'avatar')
    # ### end Alembic commands ###

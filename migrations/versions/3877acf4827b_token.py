"""token

Revision ID: 3877acf4827b
Revises: 7612da8215d4
Create Date: 2024-01-20 16:35:07.392542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3877acf4827b'
down_revision: Union[str, None] = '7612da8215d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('refresh_token', sa.String(length=255), nullable=True))
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=30),
               nullable=False)
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=255),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=20),
               nullable=True)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=30),
               nullable=True)
    op.drop_column('users', 'refresh_token')
    # ### end Alembic commands ###

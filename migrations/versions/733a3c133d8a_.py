"""empty message

Revision ID: 733a3c133d8a
Revises: 0bdebacd2c06
Create Date: 2020-04-19 08:12:50.009531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '733a3c133d8a'
down_revision = '0bdebacd2c06'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###

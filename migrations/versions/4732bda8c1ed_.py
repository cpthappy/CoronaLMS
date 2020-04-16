"""empty message

Revision ID: 4732bda8c1ed
Revises: c7968cf4263b
Create Date: 2020-04-16 20:43:06.134121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4732bda8c1ed'
down_revision = 'c7968cf4263b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('student_alias', sa.String(length=32), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    # ### end Alembic commands ###

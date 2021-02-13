"""empty message

Revision ID: 2e495b3a061f
Revises: 
Create Date: 2021-02-08 22:42:45.026149

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2e495b3a061f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('investments', sa.Column('descriptions', sa.String(length=10000), nullable=True))
    op.drop_column('investments', 'description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('investments', sa.Column('description', mysql.VARCHAR(length=10000), nullable=True))
    op.drop_column('investments', 'descriptions')
    # ### end Alembic commands ###
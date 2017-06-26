"""empty message

Revision ID: c6d8e5e1007e
Revises: 3a7638c00962
Create Date: 2017-06-16 17:08:42.888463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6d8e5e1007e'
down_revision = '3a7638c00962'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('db_page', sa.Column('publication_date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('db_page', 'publication_date')
    # ### end Alembic commands ###
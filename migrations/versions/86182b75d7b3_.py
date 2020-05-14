"""empty message

Revision ID: 86182b75d7b3
Revises: e65a9ec3b836
Create Date: 2017-10-10 11:12:36.273555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "86182b75d7b3"
down_revision = "e65a9ec3b836"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("db_page", sa.Column("additional_description", sa.TEXT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("db_page", "additional_description")
    # ### end Alembic commands ###

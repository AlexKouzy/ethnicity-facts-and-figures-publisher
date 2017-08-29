"""empty message

Revision ID: 99062ef6b9dc
Revises: 419108de3b3d
Create Date: 2017-08-24 15:38:55.526589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99062ef6b9dc'
down_revision = '419108de3b3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('db_page', sa.Column('primary_source_contact_2_email', sa.TEXT(), nullable=True))
    op.add_column('db_page', sa.Column('primary_source_contact_2_name', sa.TEXT(), nullable=True))
    op.add_column('db_page', sa.Column('primary_source_contact_2_phone', sa.TEXT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('db_page', 'primary_source_contact_2_phone')
    op.drop_column('db_page', 'primary_source_contact_2_name')
    op.drop_column('db_page', 'primary_source_contact_2_email')
    # ### end Alembic commands ###
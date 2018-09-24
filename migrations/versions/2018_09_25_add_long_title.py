"""empty message

Revision ID: 2018_09_25_add_long_title
Revises: 2018_09_24_sync_classification
Create Date: 2018-09-24 15:15:35.190282

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2018_09_25_add_long_title'
down_revision = '2018_09_24_sync_classification'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('categorisation', sa.Column('long_title', sa.String(length=255), nullable=True))

    op.get_bind()
    op.execute("""
            UPDATE categorisation SET long_title = title;
        """)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('categorisation', 'long_title')
    # ### end Alembic commands ###

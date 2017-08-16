"""empty message

Revision ID: 5382560efddb
Revises: da52de5e4530
Create Date: 2017-08-07 12:17:27.884775

"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
from application.sitebuilder.models import Build

revision = '5382560efddb'
down_revision = 'da52de5e4530'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('build_pkey', 'build', type_='primary')
    op.add_column('build', sa.Column('id', postgresql.UUID(), nullable=True))

    conn = op.get_bind()
    builds = conn.execute('SELECT * FROM build')
    for b in builds:
        conn.execute(text('UPDATE build set id = :id WHERE created_at = :created_at'),
                     id=uuid.uuid4(),
                     created_at=b['created_at'])

    op.create_primary_key('build_pkey', 'build', ['id', 'created_at'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('build_pkey', 'build', type_='primary')
    op.drop_column('build', 'id')
    op.create_primary_key('build_pkey', 'build', ['created_at'])
    # ### end Alembic commands ###
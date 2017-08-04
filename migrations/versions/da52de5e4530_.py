"""empty message

Revision ID: da52de5e4530
Revises: 4244e1e8d347
Create Date: 2017-08-04 10:47:31.652869

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'da52de5e4530'
down_revision = '4244e1e8d347'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    build_status = postgresql.ENUM('PENDING', 'STARTED', 'DONE', 'SUPERSEDED', 'FAILED', name='build_status')
    build_status.create(op.get_bind())

    op.create_table('build',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('status', postgresql.ENUM('PENDING', 'STARTED', 'DONE', 'SUPERSEDED', 'FAILED',
                                        name='build_status',
                                        create_type=False),
              nullable=False),
    sa.Column('succeeded_at', sa.DateTime(), nullable=True),
    sa.Column('failure_reason', sa.String(), nullable=True),
    sa.Column('failed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('created_at')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('build', 'status')
    op.get_bind().execute('DROP TYPE build_status')
    build_status = postgresql.ENUM('PENDING', 'STARTED', 'DONE', 'SUPERSEDED', 'FAILED', name='build_status')
    build_status.drop(op.get_bind())
    op.drop_table('build')
    # ### end Alembic commands ###
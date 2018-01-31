"""empty message

Revision ID: e0248cc6bf14
Revises: c64c6f6fb763
Create Date: 2018-01-26 11:25:14.899356

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
from application.cms.models import ArrayOfEnum

revision = 'e0248cc6bf14'
down_revision = 'c64c6f6fb763'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    uk_country_types = sa.Enum('ENGLAND', 'WALES', 'SCOTLAND', 'NORTHERN_IRELAND', 'UK', name='uk_country_types')
    uk_country_types.create(op.get_bind())

    op.add_column('page', sa.Column('area_covered', postgresql.ARRAY(uk_country_types), nullable=True))

    op.get_bind()
    op.execute("UPDATE page SET geographic_coverage = NULL WHERE TRIM(geographic_coverage) = '';")

    op.execute('''UPDATE page 
                  SET area_covered = '{"ENGLAND"}'
                  WHERE geographic_coverage = 'England';
                  ''')

    op.execute('''UPDATE page 
                  SET area_covered = '{"ENGLAND","WALES"}'
                  WHERE geographic_coverage = 'England and Wales';
                ''')

    op.execute('''UPDATE page 
                  SET area_covered = '{"ENGLAND","WALES","SCOTLAND"}'
                  WHERE geographic_coverage = 'England, Wales and Scotland';
                ''')

    op.execute('''UPDATE page 
                  SET area_covered = '{"UK"}'
                  WHERE geographic_coverage = 'UK';
               ''')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.get_bind()
    op.execute('''UPDATE page 
                  SET geographic_coverage = 'England'
                  WHERE area_covered = '{"ENGLAND"}';
                  ''')

    op.execute('''UPDATE page 
                  SET geographic_coverage = 'England and Wales'
                  WHERE area_covered = '{"ENGLAND","WALES"}';
                ''')

    op.execute('''UPDATE page 
                  SET geographic_coverage = 'England, Wales and Scotland'
                  WHERE area_covered = '{"ENGLAND","WALES","SCOTLAND"}';
                ''')

    op.execute('''UPDATE page 
                  SET geographic_coverage = 'UK'
                  WHERE area_covered = '{"UK"}';
               ''')

    op.drop_column('page', 'area_covered')
    op.execute('DROP TYPE uk_country_types')

    # ### end Alembic commands ###

"""empty message

Revision ID: 20180227_add_latest_flag_to_page
Revises: f8f8b80de743
Create Date: 2018-02-27 17:19:46.643959

"""
from functools import total_ordering

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from application.cms.models import Page

revision = '20180227_add_latest_flag_to_page'
down_revision = 'f8f8b80de743'
branch_labels = None
depends_on = None

Session = sessionmaker()
Base = declarative_base()


@total_ordering
class Page(Base):

    __tablename__ = 'page'

    guid = sa.Column(sa.String(255), nullable=False)
    version = sa.Column(sa.String(), nullable=False)
    page_type = sa.Column(sa.String(255))
    status = sa.Column(sa.String(255))
    latest = sa.Column(sa.Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('guid', 'version', name='page_guid_version_pk'),
    )

    def __eq__(self, other):
        return self.guid == other.guid and self.version == other.version

    def __hash__(self):
        return hash((self.guid, self.version))

    def __lt__(self, other):
        if self.major() < other.major():
            return True
        elif self.major() == other.major() and self.minor() < other.minor():
            return True
        else:
            return False

    def major(self):
        return int(self.version.split('.')[0])

    def minor(self):
        return int(self.version.split('.')[1])


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('page', sa.Column('latest', sa.Boolean()))

    bind = op.get_bind()
    session = Session(bind=bind)

    processed = set([])

    for page in session.query(Page).filter(Page.status=='APPROVED', Page.page_type=='measure'):
        if page.guid not in processed:
            versions = session.query(Page).filter(Page.guid==page.guid).all()
            versions.sort(reverse=True)
            for i, v in enumerate(versions):
                if i == 0:
                    v.latest = True
                else:
                    v.latest = False
                session.add(v)
            processed.add(page.guid)

    session.commit()

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('page', 'latest')
    # ### end Alembic commands ###
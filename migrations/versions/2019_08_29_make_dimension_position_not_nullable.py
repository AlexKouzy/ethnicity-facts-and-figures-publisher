"""Make the dimension position non-nullable.

Revision ID: dimension_position_not_null
Revises: 2019_05_28_mv_error_update
Create Date: 2019-08-29 16:16:59.632147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dimension_position_not_null"
down_revision = "2019_05_28_mv_error_update"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("dimension", "position", existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("dimension", "position", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###
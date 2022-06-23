"""Added author

Revision ID: 584737be295a
Revises: 
Create Date: 2022-06-19 16:03:42.806608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '584737be295a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('author', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'author')
    # ### end Alembic commands ###

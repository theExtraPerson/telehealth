"""finetuning the database

Revision ID: d848e2f0ef5a
Revises: 2c44bd5e9b5b
Create Date: 2025-05-27 19:57:01.874971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd848e2f0ef5a'
down_revision = '2c44bd5e9b5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.drop_constraint('FK__appointme__creat__76619304', type_='foreignkey')
        batch_op.drop_column('created_by')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('FK__appointme__creat__76619304', 'users', ['created_by'], ['id'])

    # ### end Alembic commands ###

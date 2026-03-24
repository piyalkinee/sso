"""add projects

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA projects')
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='projects'
    )
    op.create_table(
        'user_projects',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.users_core.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'project_id'),
        schema='projects'
    )


def downgrade() -> None:
    op.drop_table('user_projects', schema='projects')
    op.drop_table('projects', schema='projects')
    op.execute('DROP SCHEMA projects')

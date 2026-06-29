"""rename projects to projects_core

Revision ID: d4e5f6a7b8c9
Revises: b2c3d4e5f6a7
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('projects.projects') IS NOT NULL
               AND to_regclass('projects.projects_core') IS NULL THEN
                ALTER TABLE projects.projects RENAME TO projects_core;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('projects.projects_core') IS NOT NULL
               AND to_regclass('projects.projects') IS NULL THEN
                ALTER TABLE projects.projects_core RENAME TO projects;
            END IF;
        END $$;
    """)

"""reconcile oauth2 providers after legacy revision collision

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-08 19:15:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users.users_oauth2_providers (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL
                REFERENCES users.users_core(id) ON DELETE CASCADE,
            provider VARCHAR(20) NOT NULL,
            provider_user_id TEXT NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT uq_users_oauth2_provider_user
                UNIQUE (provider, provider_user_id)
        )
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('users.users_oauth') IS NOT NULL THEN
                INSERT INTO users.users_oauth2_providers
                    (user_id, provider, provider_user_id, created_at)
                SELECT user_id, provider, provider_user_id, created_at
                FROM users.users_oauth
                ON CONFLICT (provider, provider_user_id) DO NOTHING;
            END IF;
        END
        $$
        """
    )


def downgrade() -> None:
    # Keep reconciled identity links intact on downgrade.
    pass

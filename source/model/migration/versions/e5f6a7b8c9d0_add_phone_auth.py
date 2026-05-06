"""add phone auth

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-04-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Allow phone-only users (no email)
    op.alter_column('users_personal_info', 'email', schema='users', nullable=True)

    # verification_codes table for OTP
    op.execute("""
        CREATE TABLE IF NOT EXISTS access.verification_codes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users.users_core(id) ON DELETE CASCADE,
            verification_type VARCHAR(30) NOT NULL,
            recipient VARCHAR(255) NOT NULL,
            code VARCHAR(10) NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            used_at TIMESTAMP WITHOUT TIME ZONE
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_verification_codes_recipient_type
        ON access.verification_codes (recipient, verification_type)
    """)


def downgrade() -> None:
    op.drop_index('ix_verification_codes_recipient_type', table_name='verification_codes', schema='access')
    op.drop_table('verification_codes', schema='access')
    op.alter_column('users_personal_info', 'email', schema='users', nullable=False)

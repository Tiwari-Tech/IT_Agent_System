"""repair users password hash

Revision ID: 20260917_0004
Revises: 20260917_0003
Create Date: 2026-09-17
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260917_0004"
down_revision: str | None = "20260917_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)")


def downgrade() -> None:
    raise RuntimeError("Downgrade disabled: password hashes are persistent credentials.")

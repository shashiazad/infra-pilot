"""add remediation proposal

Revision ID: e3d91bf47a62
Revises: c6a7e84d15f2
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e3d91bf47a62"
down_revision: str | Sequence[str] | None = "c6a7e84d15f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "investigation_runs",
        sa.Column(
            "remediation_proposal",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "investigation_runs",
        "remediation_proposal",
    )

"""add remediation approval state

Revision ID: f92c70a34db1
Revises: e3d91bf47a62
Create Date: 2026-08-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f92c70a34db1"
down_revision: str | Sequence[str] | None = "e3d91bf47a62"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "investigation_runs",
        sa.Column("approval_status", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "investigation_runs",
        sa.Column("remediation_status", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "investigation_runs",
        sa.Column(
            "remediation_result",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("investigation_runs", "remediation_result")
    op.drop_column("investigation_runs", "remediation_status")
    op.drop_column("investigation_runs", "approval_status")

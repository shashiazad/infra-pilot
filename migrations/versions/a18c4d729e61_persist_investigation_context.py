"""persist investigation context

Revision ID: a18c4d729e61
Revises: f92c70a34db1
Create Date: 2026-08-17
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a18c4d729e61"
down_revision: str | Sequence[str] | None = "f92c70a34db1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "investigation_runs",
        sa.Column(
            "runbooks",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "investigation_runs",
        sa.Column(
            "historical_incidents",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("investigation_runs", "historical_incidents")
    op.drop_column("investigation_runs", "runbooks")

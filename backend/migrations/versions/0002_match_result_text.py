"""Widen match result storage for provider outcome payloads."""
from alembic import op
import sqlalchemy as sa

revision = "0002_match_result_text"
down_revision = "0001_multisport"
branch_labels = None
depends_on = None


def upgrade():
    # Cricsheet outcomes may contain tie, eliminator, bowl-out, method and
    # other structured fields. VARCHAR(50) silently cannot represent them.
    op.alter_column(
        "matches", "result",
        existing_type=sa.String(length=50),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade():
    # Refuse a lossy downgrade if any stored result exceeds the old limit.
    bind = op.get_bind()
    too_long = bind.execute(sa.text(
        "SELECT COUNT(*) FROM matches WHERE length(result) > 50"
    )).scalar_one()
    if too_long:
        raise RuntimeError(
            "Cannot downgrade matches.result to VARCHAR(50): "
            f"{too_long} row(s) contain longer results."
        )
    op.alter_column(
        "matches", "result",
        existing_type=sa.Text(),
        type_=sa.String(length=50),
        existing_nullable=True,
    )

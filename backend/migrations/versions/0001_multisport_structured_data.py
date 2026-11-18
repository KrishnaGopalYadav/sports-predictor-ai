"""Provider identities and structured sport statistics."""
from alembic import op
import sqlalchemy as sa

revision = "0001_multisport"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "external_identities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(80), nullable=False),
        sa.Column("sport", sa.String(30), nullable=False),
        sa.Column("entity_type", sa.String(40), nullable=False),
        sa.Column("external_id", sa.String(240), nullable=False),
        sa.Column("internal_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("provider", "sport", "entity_type", "external_id",
                            name="uq_external_identity_scope"),
    )
    op.create_table(
        "cricket_innings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("innings_number", sa.Integer(), nullable=False),
        sa.Column("batting_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("runs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wickets", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("legal_balls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extras", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("match_id", "innings_number", name="uq_cricket_innings_match_no"),
    )
    op.create_index("ix_cricket_innings_match_id", "cricket_innings", ["match_id"])
    for table, unique_name in [
        ("cricket_batting_performances", "uq_cricket_batting_player"),
        ("cricket_bowling_performances", "uq_cricket_bowling_player"),
    ]:
        if table == "cricket_batting_performances":
            op.create_table(table,
                sa.Column("id", sa.Integer(), primary_key=True),
                sa.Column("innings_id", sa.Integer(), sa.ForeignKey("cricket_innings.id", ondelete="CASCADE"), nullable=False),
                sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
                sa.Column("runs", sa.Integer(), nullable=False, server_default="0"),
                sa.Column("balls_faced", sa.Integer(), nullable=False, server_default="0"),
                sa.Column("fours", sa.Integer(), nullable=False, server_default="0"),
                sa.Column("sixes", sa.Integer(), nullable=False, server_default="0"),
                sa.Column("dismissal", sa.String(80)),
                sa.UniqueConstraint("innings_id", "player_id", name=unique_name))
        else:
            op.create_table(table,
                sa.Column("id", sa.Integer(), primary_key=True),
                sa.Column("innings_id", sa.Integer(), sa.ForeignKey("cricket_innings.id", ondelete="CASCADE"), nullable=False),
                sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
                sa.Column("legal_balls", sa.Integer(), nullable=False, server_default="0"),
                sa.Column("runs_conceded", sa.Integer(), nullable=False, server_default="0"),
                sa.Column("wickets", sa.Integer(), nullable=False, server_default="0"),
                sa.UniqueConstraint("innings_id", "player_id", name=unique_name))
        op.create_index(f"ix_{table}_innings_id", table, ["innings_id"])
    op.create_table(
        "player_team_affiliations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sport", sa.String(30), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True)),
        sa.Column("valid_to", sa.DateTime(timezone=True)),
        sa.Column("source_provider", sa.String(80), nullable=False),
        sa.Column("source_match_id", sa.String(240)),
        sa.UniqueConstraint("sport", "player_id", "team_id", "valid_from", name="uq_player_team_period"))
    op.create_index("ix_player_team_affiliations_player_id", "player_team_affiliations", ["player_id"])
    op.create_index("ix_player_team_affiliations_team_id", "player_team_affiliations", ["team_id"])
    op.create_table(
        "football_player_match_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id")),
        sa.Column("minutes_played", sa.Float(), nullable=False, server_default="0"),
        sa.Column("goals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assists", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shots", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shots_on_target", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passes_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tackles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("saves", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("match_id", "player_id", name="uq_football_player_match"))
    op.create_index("ix_football_player_match_stats_match_id", "football_player_match_stats", ["match_id"])
    op.create_index("ix_football_player_match_stats_player_id", "football_player_match_stats", ["player_id"])
    op.create_table(
        "football_match_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("home_goals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("away_goals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("home_xg", sa.Float()),
        sa.Column("away_xg", sa.Float()),
        sa.Column("source_provider", sa.String(80), nullable=False))


def downgrade():
    op.drop_table("football_match_stats")
    op.drop_index("ix_football_player_match_stats_player_id", table_name="football_player_match_stats")
    op.drop_index("ix_football_player_match_stats_match_id", table_name="football_player_match_stats")
    op.drop_table("football_player_match_stats")
    op.drop_index("ix_player_team_affiliations_team_id", table_name="player_team_affiliations")
    op.drop_index("ix_player_team_affiliations_player_id", table_name="player_team_affiliations")
    op.drop_table("player_team_affiliations")
    op.drop_index("ix_cricket_bowling_performances_innings_id", table_name="cricket_bowling_performances")
    op.drop_table("cricket_bowling_performances")
    op.drop_index("ix_cricket_batting_performances_innings_id", table_name="cricket_batting_performances")
    op.drop_table("cricket_batting_performances")
    op.drop_index("ix_cricket_innings_match_id", table_name="cricket_innings")
    op.drop_table("cricket_innings")
    op.drop_table("external_identities")

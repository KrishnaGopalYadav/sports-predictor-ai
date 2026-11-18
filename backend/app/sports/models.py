"""Sport-specific structured persistence tables.

These tables intentionally complement, rather than overload, generic MatchEvent payloads.
"""
from datetime import datetime
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ExternalIdentity(Base):
    __tablename__ = "external_identities"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    sport: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    external_id: Mapped[str] = mapped_column(String(240), nullable=False)
    internal_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("provider", "sport", "entity_type", "external_id",
                                        name="uq_external_identity_scope"),)


class CricketInnings(Base):
    __tablename__ = "cricket_innings"
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    innings_number: Mapped[int] = mapped_column(Integer, nullable=False)
    batting_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wickets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    legal_balls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extras: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    __table_args__ = (UniqueConstraint("match_id", "innings_number", name="uq_cricket_innings_match_no"),)


class CricketBattingPerformance(Base):
    __tablename__ = "cricket_batting_performances"
    id: Mapped[int] = mapped_column(primary_key=True)
    innings_id: Mapped[int] = mapped_column(ForeignKey("cricket_innings.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    balls_faced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sixes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dismissal: Mapped[str | None] = mapped_column(String(80))
    __table_args__ = (UniqueConstraint("innings_id", "player_id", name="uq_cricket_batting_player"),)


class CricketBowlingPerformance(Base):
    __tablename__ = "cricket_bowling_performances"
    id: Mapped[int] = mapped_column(primary_key=True)
    innings_id: Mapped[int] = mapped_column(ForeignKey("cricket_innings.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    legal_balls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    runs_conceded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wickets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    __table_args__ = (UniqueConstraint("innings_id", "player_id", name="uq_cricket_bowling_player"),)


class PlayerTeamAffiliation(Base):
    __tablename__ = "player_team_affiliations"
    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[str] = mapped_column(String(30), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_provider: Mapped[str] = mapped_column(String(80), nullable=False)
    source_match_id: Mapped[str | None] = mapped_column(String(240))
    __table_args__ = (UniqueConstraint("sport", "player_id", "team_id", "valid_from",
                                        name="uq_player_team_period"),)


class FootballPlayerMatchStat(Base):
    __tablename__ = "football_player_match_stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False, index=True)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    minutes_played: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    goals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assists: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shots_on_target: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passes_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tackles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    saves: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    __table_args__ = (UniqueConstraint("match_id", "player_id", name="uq_football_player_match"),)


class FootballMatchStat(Base):
    __tablename__ = "football_match_stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, unique=True)
    home_goals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    away_goals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    home_xg: Mapped[float | None] = mapped_column(Float)
    away_xg: Mapped[float | None] = mapped_column(Float)
    source_provider: Mapped[str] = mapped_column(String(80), nullable=False)

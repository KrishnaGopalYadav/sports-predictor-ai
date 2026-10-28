from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Sport(str, Enum):
    cricket = "cricket"
    football = "football"


class MatchStatus(str, Enum):
    scheduled = "scheduled"
    live = "live"
    completed = "completed"
    cancelled = "cancelled"


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[Sport] = mapped_column(SAEnum(Sport), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("sport", "name", name="uq_team_sport_name"),)
    players: Mapped[list["Player"]] = relationship(back_populates="team")


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[Sport] = mapped_column(SAEnum(Sport), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))
    role: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    team: Mapped[Optional[Team]] = relationship(back_populates="players")


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[Sport] = mapped_column(SAEnum(Sport), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[Sport] = mapped_column(SAEnum(Sport), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    season: Mapped[Optional[str]] = mapped_column(String(100))


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[Sport] = mapped_column(SAEnum(Sport), nullable=False, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    competition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competitions.id"))
    venue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("venues.id"))
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[MatchStatus] = mapped_column(SAEnum(MatchStatus), default=MatchStatus.scheduled, index=True)
    result: Mapped[Optional[str]] = mapped_column(String(50))
    raw_payload: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class MatchEvent(Base):
    __tablename__ = "match_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(200))
    sequence_no: Mapped[Optional[int]] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    payload: Mapped[Optional[str]] = mapped_column(Text)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    feature_snapshot: Mapped[Optional[str]] = mapped_column(Text)
    probability_home: Mapped[Optional[float]] = mapped_column()
    probability_draw: Mapped[Optional[float]] = mapped_column()
    probability_away: Mapped[Optional[float]] = mapped_column()
    actual_result: Mapped[Optional[str]] = mapped_column(String(50))
    log_loss: Mapped[Optional[float]] = mapped_column()
    brier_score: Mapped[Optional[float]] = mapped_column()

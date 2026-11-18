"""Cricsheet T20 JSON ZIP ingestion; raw archive members are never extracted."""
from __future__ import annotations
import argparse, json, logging, shutil, urllib.request, zipfile
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Iterator
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Competition, Match, MatchEvent, MatchStatus, Player, Sport, Team, Venue
from app.sports.models import CricketInnings, CricketBattingPerformance, CricketBowlingPerformance, PlayerTeamAffiliation, ExternalIdentity
from app.sports.cricket.aggregates import aggregate_innings

LOG = logging.getLogger("sports_predictor.ingestion.cricsheet")
DEFAULT_URL = "https://cricsheet.org/downloads/t20s_json.zip"

def read_json_members(archive_path: Path) -> Iterator[tuple[str, dict[str, Any]]]:
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            if member.is_dir() or not member.filename.lower().endswith(".json"):
                continue
            try:
                payload = json.loads(archive.read(member).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                LOG.warning("Skipping invalid JSON member %s: %s", member.filename, exc)
                continue
            if isinstance(payload, dict):
                yield Path(member.filename).name, payload

def normalize_match(filename: str, payload: dict[str, Any]) -> dict[str, Any]:
    info = payload.get("info") or {}
    teams, dates = info.get("teams") or [], info.get("dates") or []
    if len(teams) != 2 or not dates:
        raise ValueError(f"{filename}: expected two teams and a match date")
    match_date = date.fromisoformat(str(dates[0]))
    event, outcome = info.get("event") or {}, info.get("outcome") or {}
    deliveries = []
    for innings_no, innings in enumerate(payload.get("innings") or [], start=1):
        for over in innings.get("overs") or []:
            for ball_no, delivery in enumerate(over.get("deliveries") or [], start=1):
                deliveries.append({"innings": innings_no, "over": over.get("over"),
                    "delivery_in_over": ball_no, "batting_team": innings.get("team"), **delivery})
    rosters = info.get("players") or {}
    return {
        "source": "cricsheet", "source_file": filename,
        "external_id": f"cricsheet:{Path(filename).stem}", "sport": "cricket",
        "format": str(info.get("match_type") or "T20"),
        "match_date": match_date.isoformat(),
        "scheduled_at": datetime.combine(match_date, time.min, tzinfo=timezone.utc).isoformat(),
        "competition": event.get("name") or "Unknown T20 competition",
        "season": str(match_date.year), "venue": info.get("venue"),
        "teams": [str(t) for t in teams], "winner": outcome.get("winner"),
        "result": outcome, "toss": info.get("toss"), "player_rosters": rosters,
        "players": sorted({str(p) for names in rosters.values() for p in (names or [])}),
        "deliveries": deliveries, "delivery_count": len(deliveries), "raw_info": info,
        "raw_innings": payload.get("innings") or [],
    }

def validate_match(item: dict[str, Any]) -> list[str]:
    issues = []
    if len(item.get("teams", [])) != 2: issues.append("team_count_not_two")
    if item.get("winner") and item["winner"] not in item.get("teams", []): issues.append("winner_not_in_teams")
    if item.get("delivery_count", 0) <= 0: issues.append("no_deliveries")
    if item.get("format", "").upper() != "T20": issues.append("not_t20")
    return issues

def get_or_create_team(db: Session, name: str) -> Team:
    team = db.scalar(select(Team).where(Team.sport == Sport.cricket, Team.name == name))
    if team is None:
        team = Team(sport=Sport.cricket, name=name); db.add(team); db.flush()
    return team


def insert_player_team_affiliations(db: Session, rows: list[dict[str, Any]]) -> int:
    """Insert affiliations idempotently using the database's natural unique key.

    Application-side SELECT checks are insufficient here: pending rows are not
    visible when autoflush is disabled, and concurrent ingestion workers can
    race between SELECT and INSERT. The database constraint remains authoritative.
    """
    if not rows:
        return 0

    # Collapse duplicates in the current match before issuing a multi-row INSERT.
    unique_rows: dict[tuple[str, int, int, datetime | None], dict[str, Any]] = {}
    for row in rows:
        key = (row["sport"], row["player_id"], row["team_id"], row["valid_from"])
        unique_rows.setdefault(key, row)
    values = list(unique_rows.values())

    dialect = db.get_bind().dialect.name
    if dialect == "postgresql":
        statement = pg_insert(PlayerTeamAffiliation).values(values).on_conflict_do_nothing(
            constraint="uq_player_team_period"
        )
    elif dialect == "sqlite":
        statement = sqlite_insert(PlayerTeamAffiliation).values(values).on_conflict_do_nothing(
            index_elements=["sport", "player_id", "team_id", "valid_from"]
        )
    else:
        raise RuntimeError(f"Idempotent affiliation inserts are not implemented for {dialect}")
    result = db.execute(statement)
    return max(result.rowcount or 0, 0)


def persist_match(db: Session, item: dict[str, Any]) -> bool:
    provider_id = Path(item["source_file"]).stem
    identity = db.scalar(select(ExternalIdentity).where(
        ExternalIdentity.provider == "cricsheet", ExternalIdentity.sport == "cricket",
        ExternalIdentity.entity_type == "match", ExternalIdentity.external_id == provider_id))
    if identity is not None:
        return False
    existing = db.scalar(select(Match).where(Match.external_id == item["external_id"]))
    if existing is not None:
        db.add(ExternalIdentity(provider="cricsheet", sport="cricket", entity_type="match",
                                external_id=provider_id, internal_id=existing.id))
        db.flush()
        return False
    home, away = (get_or_create_team(db, n) for n in item["teams"])
    competition = db.scalar(select(Competition).where(
        Competition.sport == Sport.cricket, Competition.name == item["competition"],
        Competition.season == item["season"]))
    if competition is None:
        competition = Competition(sport=Sport.cricket, name=item["competition"], season=item["season"])
        db.add(competition); db.flush()
    venue_id = None
    if item.get("venue"):
        venue = db.scalar(select(Venue).where(Venue.sport == Sport.cricket, Venue.name == item["venue"]))
        if venue is None:
            venue = Venue(sport=Sport.cricket, name=item["venue"]); db.add(venue); db.flush()
        venue_id = venue.id
    match = Match(sport=Sport.cricket, external_id=item["external_id"],
        competition_id=competition.id, venue_id=venue_id, home_team_id=home.id, away_team_id=away.id,
        scheduled_at=datetime.fromisoformat(item["scheduled_at"]), status=MatchStatus.completed,
        result=str(item.get("winner") or json.dumps(item.get("result") or {})),
        raw_payload=json.dumps({k:v for k,v in item.items() if k not in {"deliveries","player_rosters"}}, default=str))
    db.add(match); db.flush()
    db.add(ExternalIdentity(provider="cricsheet", sport="cricket", entity_type="match",
                            external_id=provider_id, internal_id=match.id))
    player_ids = {}
    for name in item.get("players", []):
        player = db.scalar(select(Player).where(Player.sport == Sport.cricket, Player.name == name))
        if player is None:
            player = Player(sport=Sport.cricket, name=name)
            db.add(player); db.flush()
        player_ids[name] = player.id
    team_ids = {name: get_or_create_team(db, name).id for name in item["teams"]}
    match_time = datetime.fromisoformat(item["scheduled_at"])
    affiliation_rows = []
    for team_name, names in (item.get("player_rosters") or {}).items():
        team_id = team_ids.get(team_name)
        if team_id is None:
            continue
        for player_name in names or []:
            player_id = player_ids.get(player_name)
            if player_id is None:
                continue
            affiliation_rows.append({
                "sport": "cricket", "player_id": player_id, "team_id": team_id,
                "valid_from": match_time, "source_provider": "cricsheet",
                "source_match_id": provider_id,
            })
    insert_player_team_affiliations(db, affiliation_rows)
    for innings_data in aggregate_innings({"raw_innings": item.get("raw_innings", [])}):
        batting_team_id = team_ids.get(innings_data["batting_team"])
        if batting_team_id is None:
            continue
        innings_row = CricketInnings(match_id=match.id,
            innings_number=innings_data["innings_number"], batting_team_id=batting_team_id,
            runs=innings_data["runs"], wickets=innings_data["wickets"],
            legal_balls=innings_data["legal_balls"], extras=innings_data["extras"])
        db.add(innings_row); db.flush()
        for player_name, stats in innings_data["batting"].items():
            if player_name in player_ids:
                db.add(CricketBattingPerformance(innings_id=innings_row.id,
                    player_id=player_ids[player_name], **stats))
        for player_name, stats in innings_data["bowling"].items():
            if player_name in player_ids:
                db.add(CricketBowlingPerformance(innings_id=innings_row.id,
                    player_id=player_ids[player_name], **stats))
    for seq, delivery in enumerate(item["deliveries"], start=1):
        db.add(MatchEvent(match_id=match.id, sequence_no=seq, event_type="delivery",
                          payload=json.dumps(delivery, separators=(",", ":"), default=str)))
    return True

def ingest_archive(archive: Path, output: Path, load_db: bool = False) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    normalized = output / "matches.jsonl"
    counts = {"files_seen":0,"matches_normalized":0,"matches_loaded":0,
              "duplicates_skipped":0,"invalid_matches":0,"deliveries":0}
    issues: dict[str,int] = {}
    db = SessionLocal() if load_db else None
    try:
        with normalized.open("w", encoding="utf-8") as target:
            for filename, payload in read_json_members(archive):
                counts["files_seen"] += 1
                try: item = normalize_match(filename, payload)
                except (ValueError, TypeError, KeyError) as exc:
                    counts["invalid_matches"] += 1; LOG.warning("Skipping %s: %s", filename, exc); continue
                found = validate_match(item)
                for issue in found: issues[issue] = issues.get(issue,0) + 1
                if found: counts["invalid_matches"] += 1; continue
                target.write(json.dumps(item, separators=(",",":"), default=str) + "\n")
                counts["matches_normalized"] += 1; counts["deliveries"] += item["delivery_count"]
                if db is not None:
                    try:
                        inserted = persist_match(db, item); db.commit()
                        counts["matches_loaded" if inserted else "duplicates_skipped"] += 1
                    except Exception:
                        db.rollback(); LOG.exception("Database load failed for %s", filename); raise
    finally:
        if db is not None: db.close()
    manifest = {"provider":"Cricsheet","archive":archive.name,
        "generated_at":datetime.now(timezone.utc).isoformat(),"counts":counts,
        "validation_issues":issues,"normalized_file":str(normalized),"database_loaded":load_db,
        "notes":["T20 JSON adapter; deliveries stored as MatchEvent JSON payloads.",
        "Structured innings, batting, bowling, and observed player-team affiliations are persisted when --load-db is enabled."]}
    (output / "manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest

def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Cricsheet T20 JSON ZIP")
    parser.add_argument("--source",type=Path,help="Downloaded Cricsheet ZIP")
    parser.add_argument("--download",action="store_true",help="Download the Cricsheet T20 archive")
    parser.add_argument("--url",default=DEFAULT_URL)
    parser.add_argument("--output",type=Path,default=Path("/app/data/processed/cricsheet"))
    parser.add_argument("--load-db",action="store_true",help="Load normalized records into PostgreSQL")
    args = parser.parse_args()
    if bool(args.source) == bool(args.download): parser.error("provide exactly one of --source or --download")
    if args.download:
        raw = Path("/app/data/raw/cricsheet"); raw.mkdir(parents=True,exist_ok=True)
        archive = raw / "t20s_json.zip"
        request = urllib.request.Request(args.url,headers={"User-Agent":"SportsPredictorAI/0.1 research-ingestion"})
        with urllib.request.urlopen(request,timeout=120) as response, archive.open("wb") as target:
            shutil.copyfileobj(response,target)
    else:
        archive = args.source.resolve()
        if not archive.is_file(): parser.error(f"archive not found: {archive}")
    print(json.dumps(ingest_archive(archive,args.output,args.load_db),indent=2))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

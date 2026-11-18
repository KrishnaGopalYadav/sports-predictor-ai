"""Ingest local StatsBomb Open Data match/event JSON exports.

The adapter accepts a checkout/export root with data/matches and data/events folders.
It does not download data or imply commercial/redistribution rights.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any


def normalize_match(match: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    home = match.get("home_team", {}).get("home_team_name")
    away = match.get("away_team", {}).get("away_team_name")
    if not home or not away:
        raise ValueError("StatsBomb match is missing home or away team")
    home_goals = int(match.get("home_score", 0))
    away_goals = int(match.get("away_score", 0))
    players: dict[str, dict[str, Any]] = {}
    for event in events:
        player = (event.get("player") or {}).get("name")
        if not player:
            continue
        row = players.setdefault(player, {"goals": 0, "assists": 0, "shots": 0,
            "shots_on_target": 0, "passes_completed": 0, "tackles": 0, "saves": 0})
        kind = (event.get("type") or {}).get("name")
        if kind == "Shot":
            row["shots"] += 1
            shot = event.get("shot") or {}
            outcome = (shot.get("outcome") or {}).get("name")
            if outcome in {"Goal", "Saved", "Saved to Post"}:
                row["shots_on_target"] += 1
            if outcome == "Goal":
                row["goals"] += 1
        elif kind == "Pass" and (event.get("pass") or {}).get("outcome") is None:
            row["passes_completed"] += 1
        elif kind == "Duel" and (event.get("duel") or {}).get("type", {}).get("name") == "Tackle":
            row["tackles"] += 1
        elif kind == "Goal Keeper":
            row["saves"] += 1
    return {
        "provider": "statsbomb_open_data", "sport": "football",
        "external_id": str(match["match_id"]),
        "match_date": match.get("match_date"),
        "competition": (match.get("competition") or {}).get("competition_name"),
        "season": str((match.get("season") or {}).get("season_name", "")),
        "home_team": home, "away_team": away,
        "home_score": home_goals, "away_score": away_goals,
        "result": "home" if home_goals > away_goals else "away" if away_goals > home_goals else "draw",
        "venue": (match.get("stadium") or {}).get("name"),
        "events_count": len(events), "players": players,
    }


def ingest_directory(root: Path, output: Path) -> dict[str, Any]:
    matches_root = root / "data" / "matches"
    events_root = root / "data" / "events"
    if not matches_root.is_dir() or not events_root.is_dir():
        raise ValueError("expected StatsBomb Open Data layout: data/matches and data/events")
    output.mkdir(parents=True, exist_ok=True)
    normalized = output / "matches.jsonl"
    counts = {"matches_seen": 0, "matches_normalized": 0, "missing_events": 0, "invalid": 0}
    with normalized.open("w", encoding="utf-8") as target:
        for match_file in sorted(matches_root.glob("*/*.json")):
            for match in json.loads(match_file.read_text(encoding="utf-8")):
                counts["matches_seen"] += 1
                event_file = events_root / f"{match['match_id']}.json"
                if not event_file.exists():
                    counts["missing_events"] += 1
                    continue
                try:
                    item = normalize_match(match, json.loads(event_file.read_text(encoding="utf-8")))
                except (KeyError, TypeError, ValueError):
                    counts["invalid"] += 1
                    continue
                target.write(json.dumps(item, separators=(",", ":")) + "\n")
                counts["matches_normalized"] += 1
    manifest = {"provider": "StatsBomb Open Data", "counts": counts,
                "normalized_file": str(normalized),
                "notice": "Respect StatsBomb Open Data terms and attribution; this adapter is for permitted research use."}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True, help="StatsBomb Open Data checkout root")
    parser.add_argument("--output", type=Path, default=Path("/app/data/processed/statsbomb"))
    args = parser.parse_args()
    print(json.dumps(ingest_directory(args.source, args.output), indent=2))


if __name__ == "__main__":
    main()

"""Derive structured innings, batting and bowling rows from Cricsheet deliveries."""
from collections import defaultdict


def aggregate_innings(normalized_match: dict) -> list[dict]:
    result = []
    for innings_no, innings in enumerate(normalized_match.get("raw_innings", []), start=1):
        deliveries = []
        for over in innings.get("overs", []):
            for delivery in over.get("deliveries", []):
                deliveries.append(delivery)
        batting = defaultdict(lambda: {"runs": 0, "balls_faced": 0, "fours": 0, "sixes": 0, "dismissal": None})
        bowling = defaultdict(lambda: {"legal_balls": 0, "runs_conceded": 0, "wickets": 0})
        total_runs = total_extras = wickets = legal_balls = 0
        for d in deliveries:
            batter, bowler = d.get("batter"), d.get("bowler")
            runs = d.get("runs") or {}
            batter_runs = int(runs.get("batter", 0))
            total = int(runs.get("total", 0))
            extras = d.get("extras") or {}
            is_wide = int(extras.get("wides", 0)) > 0
            is_noball = int(extras.get("noballs", 0)) > 0
            total_runs += total
            total_extras += total - batter_runs
            if not is_wide:
                batting[batter]["balls_faced"] += 1
            batting[batter]["runs"] += batter_runs
            batting[batter]["fours"] += int(batter_runs == 4)
            batting[batter]["sixes"] += int(batter_runs == 6)
            bowling[bowler]["runs_conceded"] += total - int(extras.get("byes", 0)) - int(extras.get("legbyes", 0))
            if not is_wide and not is_noball:
                legal_balls += 1
                bowling[bowler]["legal_balls"] += 1
            for wicket in d.get("wickets", []):
                wickets += 1
                kind = wicket.get("kind")
                player_out = wicket.get("player_out")
                if player_out in batting:
                    batting[player_out]["dismissal"] = kind
                if kind not in {"run out", "retired hurt", "obstructing the field"}:
                    bowling[bowler]["wickets"] += 1
        result.append({
            "innings_number": innings_no,
            "batting_team": innings.get("team"),
            "runs": total_runs, "wickets": wickets, "legal_balls": legal_balls,
            "extras": total_extras,
            "batting": dict(batting), "bowling": dict(bowling),
        })
    return result

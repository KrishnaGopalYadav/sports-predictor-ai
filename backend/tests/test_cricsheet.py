import unittest
from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Player, Sport, Team
from app.sports.models import PlayerTeamAffiliation
from app.ingestion.cricsheet import (
    insert_player_team_affiliations, normalize_match, validate_match,
)


class CricsheetNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "info": {
                "match_type": "T20",
                "dates": ["2024-01-01"],
                "teams": ["Alpha", "Beta"],
                "event": {"name": "Example T20 Cup"},
                "outcome": {"winner": "Alpha"},
                "venue": "Example Ground",
                "players": {"Alpha": ["A Batter"], "Beta": ["B Bowler"]},
            },
            "innings": [{
                "team": "Alpha",
                "overs": [{
                    "over": 0,
                    "deliveries": [
                        {"batter": "A Batter", "bowler": "B Bowler", "runs": {"total": 1, "batter": 1}},
                        {"batter": "A Batter", "bowler": "B Bowler", "runs": {"total": 0, "batter": 0}},
                    ],
                }],
            }],
        }

    def test_normalizes_match_and_delivery_count(self):
        item = normalize_match("match-001.json", self.payload)
        self.assertEqual(item["sport"], "cricket")
        self.assertEqual(item["format"], "T20")
        self.assertEqual(item["teams"], ["Alpha", "Beta"])
        self.assertEqual(item["winner"], "Alpha")
        self.assertEqual(item["delivery_count"], 2)
        self.assertEqual(item["players"], ["A Batter", "B Bowler"])
        self.assertEqual(validate_match(item), [])

    def test_rejects_non_t20_format(self):
        payload = dict(self.payload)
        payload["info"] = dict(self.payload["info"], match_type="ODI")
        item = normalize_match("match-odi.json", payload)
        self.assertIn("not_t20", validate_match(item))

    def test_rejects_match_without_deliveries(self):
        payload = dict(self.payload, innings=[])
        item = normalize_match("empty.json", payload)
        self.assertIn("no_deliveries", validate_match(item))

    def test_rejects_match_with_missing_team(self):
        payload = dict(self.payload)
        payload["info"] = dict(self.payload["info"], teams=["Alpha"])
        with self.assertRaises(ValueError):
            normalize_match("bad.json", payload)



class CricsheetAffiliationPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, autoflush=False)
        self.team = Team(sport=Sport.cricket, name="Alpha")
        self.player = Player(sport=Sport.cricket, name="A Batter")
        self.db.add_all([self.team, self.player])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_duplicate_roster_entries_are_collapsed_before_insert(self):
        effective_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        row = {
            "sport": "cricket", "player_id": self.player.id, "team_id": self.team.id,
            "valid_from": effective_at, "source_provider": "cricsheet",
            "source_match_id": "match-1",
        }
        inserted = insert_player_team_affiliations(self.db, [row, dict(row)])
        self.db.commit()
        count = self.db.scalar(select(func.count()).select_from(PlayerTeamAffiliation))
        self.assertEqual(inserted, 1)
        self.assertEqual(count, 1)

    def test_reingestion_and_same_day_match_are_idempotent(self):
        effective_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
        first = {
            "sport": "cricket", "player_id": self.player.id, "team_id": self.team.id,
            "valid_from": effective_at, "source_provider": "cricsheet",
            "source_match_id": "match-1",
        }
        second = dict(first, source_match_id="match-2")
        self.assertEqual(insert_player_team_affiliations(self.db, [first]), 1)
        self.db.commit()
        self.assertEqual(insert_player_team_affiliations(self.db, [second]), 0)
        self.db.commit()
        count = self.db.scalar(select(func.count()).select_from(PlayerTeamAffiliation))
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()

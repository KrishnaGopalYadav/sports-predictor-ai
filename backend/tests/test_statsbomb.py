import unittest
from app.ingestion.statsbomb import normalize_match


class StatsBombAdapterTests(unittest.TestCase):
    def test_normalizes_football_match_and_events(self):
        match = {
            "match_id": 101,
            "match_date": "2024-01-01",
            "competition": {"competition_name": "Example League"},
            "season": {"season_name": "2023/2024"},
            "home_team": {"home_team_name": "Home FC"},
            "away_team": {"away_team_name": "Away FC"},
            "home_score": 2, "away_score": 1,
            "stadium": {"name": "Example Stadium"},
        }
        events = [
            {"type": {"name": "Shot"}, "player": {"name": "Forward"},
             "shot": {"outcome": {"name": "Goal"}}},
            {"type": {"name": "Pass"}, "player": {"name": "Midfielder"}, "pass": {}},
        ]
        item = normalize_match(match, events)
        self.assertEqual(item["sport"], "football")
        self.assertEqual(item["result"], "home")
        self.assertEqual(item["players"]["Forward"]["goals"], 1)
        self.assertEqual(item["players"]["Midfielder"]["passes_completed"], 1)


if __name__ == "__main__":
    unittest.main()

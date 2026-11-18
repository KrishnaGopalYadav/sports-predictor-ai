import unittest

from app.ingestion.cricsheet import normalize_match, validate_match


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


if __name__ == "__main__":
    unittest.main()

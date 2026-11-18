import unittest
from app.ml.baselines import cricket_match_baseline, football_match_baseline
from app.ml.evaluation import score_predictions
from app.sports.cricket.aggregates import aggregate_innings


class MultiSportMLTests(unittest.TestCase):
    def test_cricket_baseline_is_binary(self):
        result = cricket_match_baseline()
        self.assertEqual(set(result["probabilities"]), {"home", "away"})
        self.assertAlmostEqual(sum(result["probabilities"].values()), 1.0)

    def test_football_baseline_is_three_way(self):
        result = football_match_baseline()
        self.assertEqual(set(result["probabilities"]), {"home", "draw", "away"})
        self.assertAlmostEqual(sum(result["probabilities"].values()), 1.0)

    def test_cricket_innings_aggregation(self):
        result = aggregate_innings({"raw_innings": [{
            "team": "A",
            "overs": [{"over": 0, "deliveries": [
                {"batter": "B1", "bowler": "P1", "runs": {"batter": 4, "total": 4}},
                {"batter": "B1", "bowler": "P1", "runs": {"batter": 1, "total": 1},
                 "extras": {"wides": 0}},
                {"batter": "B2", "bowler": "P1", "runs": {"batter": 0, "total": 0},
                 "wickets": [{"kind": "bowled", "player_out": "B2"}]},
            ]}],
        }]})[0]
        self.assertEqual(result["runs"], 5)
        self.assertEqual(result["wickets"], 1)
        self.assertEqual(result["batting"]["B1"]["runs"], 5)
        self.assertEqual(result["bowling"]["P1"]["wickets"], 1)

    def test_football_three_class_scoring(self):
        result = score_predictions([{
            "probabilities": {"home": .5, "draw": .3, "away": .2},
            "actual_result": "home"}], sport="football")
        self.assertEqual(result["count"], 1)
        self.assertGreater(result["log_loss"], 0)


if __name__ == "__main__":
    unittest.main()

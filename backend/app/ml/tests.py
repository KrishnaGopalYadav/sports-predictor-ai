import unittest
from app.ml.baselines import cricket_match_baseline, football_match_baseline
from app.ml.evaluation import score_predictions


class BaselineTests(unittest.TestCase):
    def test_cricket_probabilities_sum_to_one(self):
        result = cricket_match_baseline()
        self.assertAlmostEqual(sum(result["probabilities"].values()), 1.0)

    def test_football_probabilities_sum_to_one(self):
        result = football_match_baseline()
        self.assertAlmostEqual(sum(result["probabilities"].values()), 1.0)
        self.assertIn("draw", result["probabilities"])

    def test_evaluation_scores_perfect_prediction(self):
        result = score_predictions([{"probabilities": {"home": .98, "draw": .01, "away": .01},
                                     "actual_result": "home"}])
        self.assertEqual(result["count"], 1)
        self.assertLess(result["log_loss"], .03)
        self.assertLess(result["brier_score"], .001)


if __name__ == "__main__":
    unittest.main()

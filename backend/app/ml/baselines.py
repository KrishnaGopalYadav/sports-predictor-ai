"""Transparent research baselines; not production-trained models."""
from math import exp, factorial


def elo_probability(home_rating: float, away_rating: float, home_advantage: float = 55.0) -> float:
    return 1.0 / (1.0 + 10.0 ** (-(home_rating + home_advantage - away_rating) / 400.0))


def cricket_match_baseline(home_rating: float = 1500, away_rating: float = 1500,
                           home_advantage: float = 55) -> dict:
    p_home = elo_probability(home_rating, away_rating, home_advantage)
    return {"sport": "cricket", "prediction_type": "match_outcome",
            "probabilities": {"home": p_home, "away": 1.0 - p_home},
            "model_version": "cricket-elo-baseline-0.1.0",
            "disclaimer": "Elo prior only; requires time-aware historical training and calibration."}


def _poisson(k: int, lam: float) -> float:
    return exp(-lam) * lam ** k / factorial(k)


def football_match_baseline(home_rating: float = 1500, away_rating: float = 1500,
                            home_advantage: float = 55) -> dict:
    # Ratings adjust simple expected-goal priors. This is a baseline heuristic, not fitted xG.
    delta = (home_rating + home_advantage - away_rating) / 400.0
    home_lambda = min(3.5, max(0.2, 1.35 * (10 ** (delta / 2))))
    away_lambda = min(3.5, max(0.2, 1.10 * (10 ** (-delta / 2))))
    scores = {(h, a): _poisson(h, home_lambda) * _poisson(a, away_lambda)
              for h in range(8) for a in range(8)}
    home = sum(p for (h, a), p in scores.items() if h > a)
    draw = sum(p for (h, a), p in scores.items() if h == a)
    away = sum(p for (h, a), p in scores.items() if h < a)
    total = home + draw + away
    return {"sport": "football", "prediction_type": "match_outcome",
            "probabilities": {"home": home / total, "draw": draw / total, "away": away / total},
            "expected_goals": {"home": home_lambda, "away": away_lambda},
            "model_version": "football-poisson-elo-baseline-0.1.0",
            "disclaimer": "Heuristic Poisson/Elo prior; expected goals are not fitted from a training set."}

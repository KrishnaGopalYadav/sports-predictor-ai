"""Shared probability scoring with sport-specific outcome spaces."""
from math import log


def score_predictions(rows: list[dict], sport: str = "football") -> dict:
    if sport not in {"cricket", "football"}:
        raise ValueError("sport must be cricket or football")
    labels = ("home", "away") if sport == "cricket" else ("home", "draw", "away")
    if not rows:
        return {"count": 0, "log_loss": None, "brier_score": None}
    log_losses, briers = [], []
    for row in rows:
        probs = row["probabilities"]
        actual = row["actual_result"]
        if actual not in labels:
            continue
        normalized = {k: max(1e-15, float(probs.get(k, 0.0))) for k in labels}
        total = sum(normalized.values())
        normalized = {k: v / total for k, v in normalized.items()}
        log_losses.append(-log(normalized[actual]))
        briers.append(sum((normalized[k] - (1.0 if k == actual else 0.0)) ** 2 for k in labels))
    if not log_losses:
        return {"count": 0, "log_loss": None, "brier_score": None}
    return {"count": len(log_losses), "log_loss": sum(log_losses) / len(log_losses),
            "brier_score": sum(briers) / len(briers), "outcome_classes": len(labels)}

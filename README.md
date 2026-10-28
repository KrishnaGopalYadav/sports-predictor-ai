# Sports Predictor AI

An experimental sports intelligence and prediction platform for cricket and football.

## Purpose

The first objective is **not public release**. The system will run privately/local-first for approximately 2–3 months against real-world match data so that we can measure:

- predictive accuracy;
- probability calibration;
- live prediction stability;
- player-performance prediction quality;
- data freshness and reliability;
- web-research quality;
- whether automated learning actually improves the model;
- failure modes and model drift.

Only after this observation period should a public product decision be made.

## Sports scope

### R1

- Cricket: T20-first.
- Football: Premier League-first.
- Pre-match win probability.
- Football: home/draw/away probabilities and expected goals.
- Cricket: win probability, expected team performance and player outcome distributions.
- Player-level performance probabilities.
- Explainable prediction factors.
- Historical backtesting and strict time-aware validation.
- Local monitoring dashboard.

### R2

- Continuous post-match ingestion.
- Automated web research for team/player news and availability.
- Evidence/provenance tracking.
- Feature freshness and confidence management.
- Automated prediction-vs-outcome evaluation.
- Error classification.
- Candidate model retraining.
- Champion/challenger model evaluation.
- Automatic promotion only when measurable validation improves.
- Live prediction updates.
- Prediction history and model version audit trail.

## Core principle

The web is a source of **new evidence**, not a substitute for statistical modelling.

```text
Web / APIs
    -> ingestion
    -> validation
    -> evidence store
    -> structured sports state
    -> feature engineering
    -> statistical/ML models
    -> calibration
    -> probability
    -> explanation/UI
    -> match outcome
    -> evaluation
    -> training dataset
    -> candidate model
```

The system must never silently change a production model merely because an LLM found a new article.

## Repository documentation

- `docs/SPORTS_PREDICTOR_DESIGN.md` — complete product, architecture, R1/R2 and 2–3 month local validation plan.

## Data philosophy

Prefer structured, licensed data providers and open datasets for model training. For cricket, Cricsheet provides structured ball-by-ball data across many international and domestic competitions. For football research, StatsBomb Open Data provides selected competitions and event/lineup data. Commercial providers such as Sportradar expose real-time feeds, lineups, player data and detailed live statistics, subject to their access and licensing terms.

## Development status

**Phase: Private research / validation — not a public prediction service.**

Accuracy claims must be based on held-out, time-aware evaluation and calibration rather than raw hit rate alone.

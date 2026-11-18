# Multi-Sport Data and ML Implementation

## Scope

This increment adds a first implementation slice for:
1. Alembic-managed sport-specific persistence tables and provider-scoped external identities.
2. Structured cricket innings, batting/bowling aggregates and player-team match affiliations.
3. A separate StatsBomb Open Data football JSON adapter.
4. Transparent cricket Elo and football Poisson/Elo baseline probability models.
5. Shared prediction persistence and probability evaluation endpoints.

It is not a claim that the platform is production-ready or that baseline probabilities are trained/calibrated.

## Database migration

The current repository still bootstraps legacy core tables with SQLAlchemy `create_all`. New sport-specific tables are introduced through Alembic.

Run from the backend container:

```bash
docker compose exec api alembic -c alembic.ini upgrade head
```

Migration `0001_multisport` adds:
- `external_identities`: unique by provider + sport + entity type + external ID;
- `cricket_innings`;
- `cricket_batting_performances`;
- `cricket_bowling_performances`;
- `player_team_affiliations`;
- `football_match_stats`;
- `football_player_match_stats`.

Do not run `docker compose down -v`; it deletes the local PostgreSQL volume.

## Cricket

The Cricsheet normalizer retains source innings and deliveries. When using `--load-db`, it writes the generic delivery events plus structured innings totals, batting and bowling rows, player-team affiliation observations, and a provider-scoped match identity.

The adapter is currently T20-only. Historical affiliations are observations tied to a source match/date, not a claim that a player remained at that club for a continuous interval.

Normalize-only command:

```bash
docker compose exec api python -m app.ingestion.cricsheet --download
```

Database load is now dependent on migration completion. Use a single importer process; inspect the manifest and database before any repeated bulk run.

## Football

The StatsBomb adapter reads an existing Open Data checkout/export with:
- `data/matches/{competition_id}/{season_id}.json`;
- `data/events/{match_id}.json`.

Example:

```bash
docker compose exec api python -m app.ingestion.statsbomb --source /app/data/raw/statsbomb
```

It writes normalized JSONL and a manifest under `/app/data/processed/statsbomb`. It does not download data, load football rows into PostgreSQL, or guarantee full player-stat coverage yet. Dataset coverage and terms/attribution must be checked before use or redistribution.

## Baseline models

- Cricket: Elo-style binary home/away prior with a configurable home advantage.
- Football: Elo-adjusted Poisson score prior producing home/draw/away probabilities and expected goals.

These are transparent starting points, not trained models. Do not present them as reliable forecasts until historical training, walk-forward validation and calibration are implemented.

## APIs

- `POST /api/v1/predictions/baseline`: JSON body `{"sport":"cricket"|"football","home_rating":1500,"away_rating":1500}`.
- `POST /api/v1/predictions`: persist a match-linked prediction and feature snapshot.
- `GET /api/v1/predictions/{match_id}`: list prediction snapshots.
- `POST /api/v1/evaluation/score`: score supplied outcomes using sport-appropriate Log Loss and Brier Score.

Football evaluation uses multiclass home/draw/away scoring. Cricket evaluation uses binary home/away scoring.

## Verification

```bash
docker compose exec api python -m unittest discover -s tests -v
docker compose exec api alembic -c alembic.ini upgrade head
curl http://localhost:8000/api/v1/meta
```

The user must run these against their local database and report output. Do not run the importer with `--load-db` until the migration has succeeded and the dataset has been reviewed.

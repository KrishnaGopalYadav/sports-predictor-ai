# Repository Audit — 14 November 2026

Repository: `KrishnaGopalYadav/sports-predictor-ai`  
Branch audited: `main`  
Audit basis: source files retrieved from the GitHub default branch during this review. This is a source audit, not a test run against the user's local Docker environment.

## Confirmed foundation

- Docker Compose defines PostgreSQL 16, FastAPI and Next.js.
- PostgreSQL has a persistent named volume and a health check.
- The API waits for PostgreSQL health and exposes port 8000.
- The frontend exposes port 3000 and calls the API through `NEXT_PUBLIC_API_BASE_URL`.
- FastAPI exposes `/`, `/health` and `/api/v1/meta`.
- SQLAlchemy models exist for Team, Player, Venue, Competition, Match, MatchEvent and Prediction.
- `.gitignore` excludes local raw/processed/features data and model artifacts.
- Alembic is present in Python requirements, but the audited tree does not contain `backend/alembic.ini` or a migration environment.
- API startup currently invokes `Base.metadata.create_all()`, documented as temporary.

## Gaps before model work

1. No historical ingestion adapter existed on the audited main branch.
2. No verified historical dataset coverage report existed.
3. The schema has no provider-identity mapping table and Match.external_id is not unique.
4. Ball-by-ball data has no typed delivery/innings schema; MatchEvent stores free-form JSON text.
5. Player team association is a single optional team_id and cannot represent historical transfers/rosters reliably.
6. No dedicated innings, batting, bowling or player-match aggregate tables were found in the audited models.
7. No prediction training/evaluation pipeline or model registry was confirmed in the audited backend files.
8. No dedicated frontend ML dashboard or prediction workflow was verified by this focused audit.

## Risks and controls

- Do not start concurrent imports until external ID uniqueness is enforced with a database migration.
- Keep raw provider files locally and out of Git.
- Preserve source IDs and provenance; never treat scraped claims as ground truth without validation.
- Use time-aware/walk-forward validation before model training.
- Treat current player names and team membership as provisional identity data; disambiguation and historical roster modelling remain future work.

## Phase 1.5 work on this feature branch

This branch adds a first Cricsheet T20 JSON ZIP adapter. It normalizes match metadata and deliveries, emits JSONL and a manifest, supports optional PostgreSQL loading, and includes unit tests for basic normalization/validation. It intentionally does not claim football ingestion, full cricket statistics, Alembic migrations, or prediction modelling are complete.

## Local verification

Run unit tests inside the API container:

```bash
docker compose exec api python -m unittest discover -s tests -v
```

Run ingestion in normalize-only mode first:

```bash
docker compose exec api python -m app.ingestion.cricsheet --download
```

Inspect the manifest and JSONL under host `data/processed/cricsheet/`. Only after reviewing counts and samples should the database load be enabled:

```bash
docker compose exec api python -m app.ingestion.cricsheet --download --load-db
```

## Acceptance criteria for this increment

- Tests pass.
- Archive parsing completes without extracting ZIP members.
- Manifest includes input, normalized match, delivery, invalid-record and validation-issue counts.
- Normalized JSONL is readable and retained locally.
- Optional DB load creates completed cricket matches and delivery events and skips already imported external IDs in sequential runs.

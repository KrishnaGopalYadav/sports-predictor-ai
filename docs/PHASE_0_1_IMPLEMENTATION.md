# Phase 0 & Phase 1 Implementation

## Objective

Phase 0 establishes a reproducible local Docker environment. Phase 1 establishes the canonical PostgreSQL data model that will be used by historical ingestion, prediction, evaluation, and the later R2 self-learning pipeline.

## Current services

- `frontend`: Next.js development server on port 3000.
- `api`: FastAPI on port 8000.
- `postgres`: PostgreSQL 16 on port 5432.

## Canonical entities

The initial schema contains:

- Sport
- Competition
- Season (represented initially on Competition)
- Team
- Player
- Venue
- Match
- MatchEvent
- Prediction

The model is intentionally provider-neutral. External provider IDs and raw payloads belong at the ingestion boundary; the prediction engine should consume normalized canonical entities.

## Important design decisions

1. PostgreSQL is the source of truth for structured application data.
2. Raw external data will be retained under the local `data/` area during research, while normalized records live in PostgreSQL.
3. Predictions contain a feature snapshot so future evaluation can reconstruct what the model knew at prediction time.
4. `model_version` is stored with every prediction to make R1/R2 comparisons reproducible.
5. Web research and evidence tables will be added before R2; the LLM will not directly modify model weights.
6. The current `create_all` startup bootstrap is deliberately temporary. Alembic migrations will replace it before historical ingestion/R1 development.

## Next implementation step

Build the provider adapter interfaces and historical ingestion pipeline, starting with T20 cricket and Premier League football. Load raw data, normalize it into the canonical schema, and add data-quality checks before any prediction model is trained.

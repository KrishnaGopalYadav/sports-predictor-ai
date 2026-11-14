# Phase 1.5 — Historical Data Ingestion

## First increment: Cricsheet T20

This increment adds a Cricsheet JSON ZIP adapter that reads archive members without extracting them, normalizes match metadata and ball-by-ball deliveries, validates basic match integrity, writes JSONL plus a manifest, and optionally loads records into the existing PostgreSQL tables.

## Run locally

Download and normalize, without database writes:

    docker compose exec api python -m app.ingestion.cricsheet --download

Download, normalize and load into PostgreSQL:

    docker compose exec api python -m app.ingestion.cricsheet --download --load-db

Use an archive already present under the mounted data directory:

    docker compose exec api python -m app.ingestion.cricsheet --source /app/data/raw/cricsheet/t20s_json.zip --load-db

Output defaults to /app/data/processed/cricsheet/matches.jsonl and manifest.json. The archive is stored in /app/data/raw/cricsheet/. The Compose file mounts host ./data at /app/data, and data/ is gitignored.

## Schema limitations identified by the audit

- Deliveries are stored as MatchEvent.payload JSON text.
- Player rows are created by name, but historical team affiliation is not assigned because players can change teams.
- Dedicated innings, batting, bowling, dismissal, extras, playing-XI and player-team-history tables are still needed.
- Match.external_id is indexed but not unique. The loader checks before insert; run one importer process at a time until migrations and uniqueness constraints are added.
- Backend startup still calls Base.metadata.create_all(). Alembic migrations should replace this before production-grade ingestion.

## Data-quality and licensing

Malformed JSON and matches failing basic validation are skipped and counted in the manifest. This does not guarantee complete coverage. Review Cricsheet's current terms and attribution requirements before redistribution or public/commercial use.

## Acceptance checks

1. Archive parses without filesystem extraction.
2. Manifest reports files, normalized matches, deliveries, invalid records and issue counts.
3. Re-running with --load-db skips existing Cricsheet external IDs.
4. PostgreSQL contains completed cricket matches and delivery events.
5. Normalized JSONL remains available for independent inspection.

## Next work

Add migrations and provider-ID uniqueness, dedicated cricket aggregates/player-team history, fixture-based tests, coverage reporting, and then a football adapter after confirming dataset licensing and field coverage.

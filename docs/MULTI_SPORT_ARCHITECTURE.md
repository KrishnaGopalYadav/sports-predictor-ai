# Multi-Sport Architecture — Cricket and Football First

**Status:** Architecture foundation  
**Initial sports:** Cricket and Football  
**Extension goal:** Add future sports without changing shared platform workflows.

## 1. Architectural decision

Sports Predictor AI is one platform with a shared application core and isolated sport domains. It is not two unrelated applications, and it is not one generic sports model.

The initial registry enables cricket and football. Sport-specific ingestion, domain data, feature engineering and models remain separate because the rules and statistical meaning of events differ substantially.

## 2. Logical architecture

```text
                    Sports Predictor AI
                            |
             +--------------+--------------+
             |                             |
        Shared Platform              Sport Registry
             |                             |
  +----------+-----------+          +------+------+
  |          |           |          |             |
Users     Matches    Predictions  Cricket       Football
  |          |           |          |             |
  +----------+-----------+       Cricket       Football
             |                  ingestion     ingestion
      Model/Evaluation             |             |
       and Audit APIs          Cricket data  Football data
             |                  features      features
       Shared metrics              |             |
             +---------------------+-------------+
                                   |
                         Sport-specific models
                                   |
                         Common prediction contract
```

## 3. Shared platform responsibilities

The shared core owns:
- users and authentication;
- sport identity and sport-aware entity references;
- competitions, seasons, teams, players and venues;
- fixtures and match lifecycle;
- source provenance and ingestion-run metadata;
- prediction records and immutable feature snapshots;
- model versions, training runs and evaluation results;
- common APIs, authorization, observability and UI navigation.

A shared entity must always be scoped by sport. Provider identifiers must be scoped by provider and sport, not assumed globally unique.

## 4. Sport-specific responsibilities

### Cricket domain

Cricket-specific concepts belong under `app/sports/cricket`:
- format (T20, ODI, Test and later other formats);
- innings and batting/bowling innings;
- overs and deliveries;
- batter, bowler, fielder and dismissal roles;
- extras, wickets, powerplays and innings state;
- batting and bowling performance aggregates;
- cricket-specific features and prediction targets.

The existing Cricsheet adapter remains a cricket ingestion adapter. It must not become a generic match-event parser.

### Football domain

Football-specific concepts belong under `app/sports/football`:
- competition and season-specific match rules;
- periods and match clock;
- starting lineups, substitutes and player minutes;
- goals, assists, shots, cards, corners and substitutions;
- goalkeeper and outfield player statistics;
- xG/xA and football-specific features and targets.

Football ingestion will be added as a separate adapter after dataset coverage and licensing are checked. StatsBomb Open Data is a candidate for research/backtesting, not a blanket assumption of production or redistribution rights.

## 5. Common prediction contract

Both sport models should eventually return a common envelope while retaining sport-specific output details:

```json
{
  "sport": "football",
  "match_id": "internal-match-id",
  "model_version": "football-1.0.0",
  "prediction_type": "match_outcome",
  "generated_at": "timestamp",
  "probabilities": {
    "home": 0.48,
    "draw": 0.27,
    "away": 0.25
  },
  "sport_specific": {
    "expected_goals_home": 1.6,
    "expected_goals_away": 1.1
  },
  "feature_snapshot_id": "immutable-snapshot-id"
}
```

Cricket may return win probability and innings/player distributions; football may return 1X2, scoreline and player event probabilities. The shared envelope standardizes identity, provenance and versioning, not the underlying statistical targets.

## 6. Model isolation

- Train and evaluate models independently by sport.
- Keep sport-specific features and target definitions in their domain modules.
- Never train a single model by mixing raw cricket and football event rows.
- Shared model infrastructure may handle experiment tracking, artifact storage, versioning and evaluation orchestration.
- A model is promoted only against its own sport-specific baselines and time-aware validation.

## 7. Current implementation boundary

This increment adds a metadata registry and package boundaries for cricket and football. It does **not** claim that football ingestion, football statistics, either sport's prediction model, or model training is implemented.

The existing SQLAlchemy entities already include a `sport` field on core entities and the current `Sport` enum contains cricket and football. The registry complements that persistence model; it does not replace it.

## 8. Next implementation sequence

1. Add provider identity and database uniqueness constraints through Alembic migrations.
2. Define typed normalized match/event contracts shared only at the ingestion boundary.
3. Harden Cricsheet ingestion, add coverage reports and cricket-specific structured tables.
4. Add a separate football historical adapter after validating dataset schema, coverage and terms.
5. Build sport-specific baseline feature pipelines and models.
6. Expose the common prediction envelope and shared evaluation APIs.
7. Add player-performance models independently for each sport.

## 9. Extension rule

A future sport should be added by:
1. registering its sport identity;
2. creating a new `app/sports/<sport>` domain package;
3. implementing its own provider adapters and normalized domain records;
4. adding sport-specific feature/target/model tests;
5. reusing shared prediction, provenance, model-version and evaluation services.

Adding a sport must not require changes to cricket or football event semantics.

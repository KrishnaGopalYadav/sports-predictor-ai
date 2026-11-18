import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, Prediction
from app.api.schemas import EvaluationRequest, PredictionCreate, PredictionRead
from app.ml.evaluation import score_predictions
from app.ml.baselines import cricket_match_baseline, football_match_baseline

router = APIRouter(prefix="/api/v1", tags=["predictions", "evaluation"])


@router.post("/predictions/baseline")
def get_baseline(payload: dict):
    sport = payload.get("sport")
    home_rating = float(payload.get("home_rating", 1500))
    away_rating = float(payload.get("away_rating", 1500))
    if sport == "cricket":
        return cricket_match_baseline(home_rating, away_rating)
    if sport == "football":
        return football_match_baseline(home_rating, away_rating)
    raise HTTPException(status_code=400, detail="sport must be cricket or football")


@router.post("/predictions", response_model=PredictionRead, status_code=201)
def create_prediction(payload: PredictionCreate, db: Session = Depends(get_db)):
    match = db.get(Match, payload.match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="match not found")
    row = Prediction(
        match_id=payload.match_id,
        model_version=payload.model_version,
        feature_snapshot=json.dumps(payload.feature_snapshot),
        probability_home=payload.probability_home,
        probability_draw=payload.probability_draw,
        probability_away=payload.probability_away,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/predictions/{match_id}", response_model=list[PredictionRead])
def list_predictions(match_id: int, db: Session = Depends(get_db)):
    if db.get(Match, match_id) is None:
        raise HTTPException(status_code=404, detail="match not found")
    return db.query(Prediction).filter(Prediction.match_id == match_id).order_by(Prediction.created_at.desc()).all()


@router.post("/evaluation/score")
def evaluate(payload: EvaluationRequest):
    result = score_predictions([row.model_dump() for row in payload.rows])
    return {"sport": payload.sport, **result}

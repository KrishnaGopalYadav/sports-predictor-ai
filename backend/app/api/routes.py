from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, Prediction
from app.api.schemas import EvaluationRequest, PredictionCreate, PredictionRead
from app.ml.evaluation import score_predictions

router = APIRouter(prefix="/api/v1", tags=["predictions", "evaluation"])


@router.post("/predictions", response_model=PredictionRead, status_code=201)
def create_prediction(payload: PredictionCreate, db: Session = Depends(get_db)):
    match = db.get(Match, payload.match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="match not found")
    row = Prediction(
        match_id=payload.match_id,
        model_version=payload.model_version,
        feature_snapshot=__import__("json").dumps(payload.feature_snapshot),
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

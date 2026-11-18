from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class PredictionCreate(BaseModel):
    match_id: int
    model_version: str = Field(min_length=1, max_length=100)
    probability_home: float = Field(ge=0, le=1)
    probability_draw: float | None = Field(default=None, ge=0, le=1)
    probability_away: float = Field(ge=0, le=1)
    feature_snapshot: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def probabilities_sum_to_one(self):
        values = [self.probability_home, self.probability_away]
        if self.probability_draw is not None:
            values.append(self.probability_draw)
        if abs(sum(values) - 1.0) > 1e-6:
            raise ValueError("outcome probabilities must sum to 1")
        return self


class PredictionRead(BaseModel):
    id: int
    match_id: int
    model_version: str
    created_at: datetime
    probability_home: float | None
    probability_draw: float | None
    probability_away: float | None
    actual_result: str | None

    model_config = {"from_attributes": True}


class EvaluationRow(BaseModel):
    probabilities: dict[Literal["home", "draw", "away"], float]
    actual_result: Literal["home", "draw", "away"]


class EvaluationRequest(BaseModel):
    sport: Literal["cricket", "football"]
    rows: list[EvaluationRow]

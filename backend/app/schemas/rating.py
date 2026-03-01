"""Rating Pydantic schemas."""
from pydantic import BaseModel
from datetime import datetime


class RatingCreate(BaseModel):
    job_id: int
    score: int  # 1-5
    comment: str | None = None


class RatingResponse(BaseModel):
    id: int
    job_id: int
    client_id: int
    artisan_id: int
    score: int
    comment: str | None
    created_at: datetime

    class Config:
        from_attributes = True

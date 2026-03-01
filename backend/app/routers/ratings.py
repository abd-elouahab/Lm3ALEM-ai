"""Ratings: client submits rating after job."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.models import User, Rating, Job, Client, Artisan
from app.models.enums import JobStatusEnum
from app.auth import get_current_user
from app.schemas.rating import RatingCreate, RatingResponse
from app.services.ranking_service import recalculate_ranking_score

router = APIRouter()


def _get_client_id(db: Session, user: User) -> int | None:
    c = db.query(Client).filter(Client.user_id == user.id).first()
    return c.id if c else None


@router.post("/", response_model=RatingResponse)
def create_rating(
    body: RatingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    client_id = _get_client_id(db, current_user)
    if not client_id:
        raise HTTPException(status_code=403, detail="Only clients can rate")
    if body.score < 1 or body.score > 5:
        raise HTTPException(status_code=400, detail="Score must be 1-5")
    job = db.query(Job).filter(Job.id == body.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.client_id != client_id:
        raise HTTPException(status_code=403, detail="Not your job")
    if job.status != JobStatusEnum.completed:
        raise HTTPException(status_code=400, detail="Job must be completed first")
    if not job.artisan_id:
        raise HTTPException(status_code=400, detail="Job has no artisan")
    existing = db.query(Rating).filter(Rating.job_id == body.job_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already rated")
    rating = Rating(
        job_id=body.job_id,
        client_id=client_id,
        artisan_id=job.artisan_id,
        score=body.score,
        comment=body.comment,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    recalculate_ranking_score(db, job.artisan_id)
    return rating


@router.get("/{artisan_id}")
def get_ratings(artisan_id: int, db: Session = Depends(get_db)):
    ratings = db.query(Rating).filter(Rating.artisan_id == artisan_id).all()
    return {"ratings": [{"score": r.score, "comment": r.comment, "created_at": r.created_at} for r in ratings]}

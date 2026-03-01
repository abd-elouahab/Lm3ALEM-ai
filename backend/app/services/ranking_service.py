"""Ranking: recalculate artisan score and level after completed+rated job."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Artisan, Rating, Job, JobStatusEnum


def _normalize_rating_score(score: float) -> float:
    """Out of 5 -> 0-1."""
    return max(0, min(1, score / 5.0))


def recalculate_ranking_score(db: Session, artisan_id: int) -> float:
    """
    new_score = (
        rating.score * 0.40 +      # quality (out of 5, normalized)
        on_time_ratio * 0.25 +     # reliability
        response_rate * 0.15 +     # communication
        price_satisfaction * 0.10 + # value for money
        creativity_bonus * 0.10    # bonus for 5-star comments
    ) * 20  # scale to 0-100
    """
    artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    if not artisan:
        return 0.0
    ratings = db.query(Rating).filter(Rating.artisan_id == artisan_id).all()
    if not ratings:
        return float(artisan.ranking_score)

    # Quality: average of last ratings, normalized
    avg_score = sum(r.score for r in ratings) / len(ratings)
    quality = _normalize_rating_score(avg_score)

    # Placeholders when no extra data: assume good
    on_time_ratio = 0.9
    response_rate = 0.9
    price_satisfaction = 0.85
    creativity_bonus = 0.0
    for r in ratings:
        if r.score == 5 and r.comment and len(r.comment.strip()) > 10:
            creativity_bonus = 0.2
            break

    raw = (
        quality * 0.40
        + on_time_ratio * 0.25
        + response_rate * 0.15
        + price_satisfaction * 0.10
        + (0.10 + creativity_bonus) * 0.10
    )
    new_score = raw * 20
    new_score = max(0, min(100, new_score))
    artisan.ranking_score = round(new_score, 2)
    db.commit()
    return artisan.ranking_score


def get_artisan_level(artisan: Artisan) -> str:
    """
    Apprenti: score < 60 or total_jobs < 5
    Compagnon: score >= 60 and total_jobs >= 5
    Maitre Artisan: score >= 75 and total_jobs >= 20
    Maitre Maalem: score >= 90 and total_jobs >= 50
    """
    s = artisan.ranking_score or 0
    j = artisan.total_jobs or 0
    if s >= 90 and j >= 50:
        return "Maitre Maalem"
    if s >= 75 and j >= 20:
        return "Maitre Artisan"
    if s >= 60 and j >= 5:
        return "Compagnon"
    return "Apprenti"

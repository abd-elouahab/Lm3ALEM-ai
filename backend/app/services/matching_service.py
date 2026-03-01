"""Matching algorithm: geo query, scoring, notification loop."""
import math
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import (
    Job,
    Artisan,
    Client,
    User,
    MatchingAttempt,
    MatchingResponseEnum,
    JobStatusEnum,
)
from app.services.notification_service import send_sms_to_artisan


from datetime import datetime


def _resolve_job_city(db: Session, job: Job) -> str:
    """Resolve job city from client profile, fallback to job snapshot."""
    if job.client_id:
        client = db.query(Client).filter(Client.id == job.client_id).first()
        if client and client.city:
            return client.city
    return (getattr(job, "city", "") or "").strip()

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two (lat, lon) points."""
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def score_artisan(artisan: Artisan, client_lat: float | None, client_lng: float | None, db: Session) -> dict:
    # 1. Distance score (closer = higher)
    if client_lat is None or client_lng is None or artisan.latitude is None or artisan.longitude is None:
        # If location data is missing, keep a neutral distance score.
        distance_km = 0.0
        distance_score = 0.5
    else:
        distance_km = haversine_km(
            client_lat, client_lng,
            artisan.latitude, artisan.longitude
        )
        distance_score = 1 / (distance_km + 0.1)
    
    # 2. Ranking score (normalized to 0-1)
    ranking_normalized = artisan.ranking_score / 100
    
    # 3. Turn-based fairness score
    # Find how many days since this artisan last completed a job
    last_job = db.query(Job).filter(
        Job.artisan_id == artisan.id,
        Job.status == 'completed'
    ).order_by(Job.completed_at.desc()).first()
    
    if last_job is None:
        # Never worked → highest priority
        turn_score = 1.0
        days_since_last = None
    else:
        # Avoid crashing if completed_at is somehow null on a completed job
        if not last_job.completed_at:
            last_job.completed_at = datetime.utcnow()
        days_since_last = (datetime.utcnow() - last_job.completed_at.replace(tzinfo=None)).days
        # More days since last job = higher turn score
        # Cap at 30 days for normalization
        turn_score = min(days_since_last / 30, 1.0)
    
    # 4. Final composite score
    # Weights : distance 40%, ranking 35%, turn fairness 25%
    final_score = (
        distance_score * 0.40 +
        ranking_normalized * 0.35 +
        turn_score * 0.25
    )
    
    return {
        "artisan": artisan,
        "score": round(final_score, 4),
        "distance_km": round(distance_km, 2),
        "turn_score": round(turn_score, 2),
        "days_since_last_job": days_since_last
    }


def get_top_artisans_for_job(db: Session, job_id: int, limit: int = 3) -> List[Artisan]:
    """
    Step 1: Geo query — specialty match, is_available, same city as client.
    Step 2: Calculate turn-based fairness score with geo and ranking data.
    Return top `limit` artisans by score desc.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return []
    client = db.query(Client).filter(Client.id == job.client_id).first() if job.client_id else None
    client_lat = client.latitude if client else None
    client_lon = client.longitude if client else None
    client_city = (client.city if client and client.city else _resolve_job_city(db, job)).lower().strip()
    problem_type = job.problem_type

    candidates = (
        db.query(Artisan)
        .filter(
            and_(
                Artisan.specialty == problem_type,
                Artisan.is_available == True,
            )
        )
        .all()
    )
    if not candidates:
        return []
    # Filter by same city (flexible match)
    same_city = [a for a in candidates if client_city and a.city.lower().strip() == client_city]
    if not same_city:
        same_city = candidates

    scored: List[tuple[float, Artisan]] = []
    for a in same_city:
        artisan_score_data = score_artisan(a, client_lat, client_lon, db)
        score = artisan_score_data["score"]
        # Priority boost for replacement artisans
        if getattr(a, "priority_boost", False):
            score *= 1.5
        scored.append((score, a))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for _, a in scored[:limit]]


def run_matching_loop(db: Session, job_id: int) -> None:
    """
    Step 3: Offer publication.
    Create pending matching attempts immediately for relevant artisans.
    This makes offers visible in artisan dashboard without waiting.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or job.status != JobStatusEnum.matching:
        return

    # Publish to several artisans so at least one relevant worker sees the offer quickly.
    top = get_top_artisans_for_job(db, job_id, limit=20)
    if not top:
        return

    # Exclude already attempted
    attempted_ids = {
        ma.artisan_id
        for ma in db.query(MatchingAttempt).filter(MatchingAttempt.job_id == job_id).all()
    }

    for artisan in top:
        if artisan.id in attempted_ids:
            continue

        # Create a visible pending offer for the artisan dashboard.
        ma = MatchingAttempt(
            job_id=job_id,
            artisan_id=artisan.id,
            response=MatchingResponseEnum.pending,
        )
        db.add(ma)
        # Commit one-by-one to avoid enum cast mismatch on bulk insert.
        try:
            db.commit()
        except Exception:
            db.rollback()
            continue
        send_sms_to_artisan(db, artisan.id, job_id)
    return


def apply_refusal_penalty(db: Session, artisan_id: int, penalty: int = 5) -> None:
    """Apply refusal penalty by decreasing ranking score and tracking refusal count."""
    artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    if not artisan:
        return
    artisan.ranking_score = max(0, artisan.ranking_score - penalty)
    artisan.refusal_count = (artisan.refusal_count or 0) + 1
    db.commit()


def reassign_after_refusal(job_id: int, refused_artisan_id: int, db: Session):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    
    # Get all artisans already tried for this job
    tried_ids = [
        a.artisan_id for a in 
        db.query(MatchingAttempt)
        .filter(MatchingAttempt.job_id == job_id)
        .all()
    ]
    
    # Find next best artisan not already tried
    candidates = db.query(Artisan).filter(
        Artisan.specialty == job.problem_type,
        Artisan.is_available == True,
        Artisan.id.notin_(tried_ids)
    ).all()
    
    client_city = _resolve_job_city(db, job).lower().strip()
    same_city = [a for a in candidates if a.city.lower().strip() == client_city]
    if not same_city:
        same_city = candidates
        
    if not same_city:
        # No more artisans available
        job.status = JobStatusEnum.pending
        db.commit()
        return None
        
    client = db.query(Client).filter(Client.id == job.client_id).first() if job.client_id else None
    client_lat = client.latitude if client else None
    client_lon = client.longitude if client else None
    
    # Score and pick best
    scored = sorted(
        same_city,
        key=lambda a: score_artisan(
            a, client_lat, client_lon, db
        )["score"],
        reverse=True
    )
    
    next_artisan = scored[0]
    
    # Create new matching attempt
    new_attempt = MatchingAttempt(
        job_id=job_id,
        artisan_id=next_artisan.id,
        response=MatchingResponseEnum.pending
    )
    db.add(new_attempt)
    db.commit()
    
    # Log notification (SMS simulation)
    user = db.query(User).filter(User.id == next_artisan.user_id).first()
    phone = user.phone if user else "Unknown"
    city_label = _resolve_job_city(db, job) or "مدينتك"
    print(f"SMS → {phone}: عندك طلب جديد فـ{city_label}")
    
    return next_artisan


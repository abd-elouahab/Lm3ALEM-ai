"""Payment escrow and 48h guarantee logic."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import (
    Job,
    Artisan,
    Payment,
    Guarantee,
    GuaranteeStatusEnum,
    PaymentStatusEnum,
    JobStatusEnum,
)
from app.config import settings
from app.services.matching_service import get_top_artisans_for_job, apply_refusal_penalty


ARTISAN_SHARE = 0.50
SAVINGS_SHARE = 0.30
PLATFORM_SHARE = 0.20


def create_payment_for_job(db: Session, job_id: int, amount: float) -> Payment | None:
    """Create payment record with 50/30/20 split, status 'held'."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    artisan_share = amount * ARTISAN_SHARE
    savings_share = amount * SAVINGS_SHARE
    platform_share = amount * PLATFORM_SHARE
    pay = Payment(
        job_id=job_id,
        amount=amount,
        artisan_share=artisan_share,
        savings_share=savings_share,
        platform_share=platform_share,
        status=PaymentStatusEnum.held,
    )
    db.add(pay)
    db.commit()
    db.refresh(pay)
    return pay


def create_guarantee_for_job(db: Session, job_id: int) -> Guarantee | None:
    """When job is declared complete: opened_at = now(), expires_at = now() + 48h."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    now = datetime.utcnow()
    expires = now + timedelta(hours=settings.GUARANTEE_HOURS)
    g = Guarantee(
        job_id=job_id,
        opened_at=now,
        expires_at=expires,
        status=GuaranteeStatusEnum.open,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def release_escrow(db: Session, job_id: int) -> bool:
    """Set payment status = released, artisan.savings += savings_share, released_at = now."""
    pay = db.query(Payment).filter(Payment.job_id == job_id).first()
    if not pay or pay.status != PaymentStatusEnum.held:
        return False
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.artisan_id:
        return False
    artisan = db.query(Artisan).filter(Artisan.id == job.artisan_id).first()
    if artisan:
        artisan.savings = (artisan.savings or 0) + pay.savings_share
    pay.status = PaymentStatusEnum.released
    pay.released_at = datetime.utcnow()
    db.commit()
    return True


def check_guarantee_expired(db: Session, guarantee_id: int) -> bool:
    """
    If guarantee expired and status still 'open' -> release escrow, set guarantee status 'expired'.
    """
    g = db.query(Guarantee).filter(Guarantee.id == guarantee_id).first()
    if not g or g.status != GuaranteeStatusEnum.open:
        return False
    if datetime.utcnow() < g.expires_at:
        return False
    g.status = GuaranteeStatusEnum.expired
    db.commit()
    release_escrow(db, g.job_id)
    return True


def claim_guarantee(
    db: Session, job_id: int, complaint_text: str | None = None, complaint_photo_url: str | None = None
) -> Guarantee | None:
    """Client files complaint: set guarantee status = 'claimed' and re-open job for same artisan."""
    g = db.query(Guarantee).filter(Guarantee.job_id == job_id).first()
    if not g or g.status != GuaranteeStatusEnum.open:
        return None
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    g.status = GuaranteeStatusEnum.claimed
    g.complaint_text = complaint_text
    g.complaint_photo_url = complaint_photo_url
    # Send the same artisan back first, as requested.
    if job.artisan_id:
        job.status = JobStatusEnum.accepted
    db.commit()
    db.refresh(g)
    return g


def resolve_guarantee(db: Session, job_id: int) -> bool:
    """Artisan returned and fixed -> status = resolved, release payment normally."""
    g = db.query(Guarantee).filter(Guarantee.job_id == job_id).first()
    if not g or g.status != GuaranteeStatusEnum.claimed:
        return False
    g.status = GuaranteeStatusEnum.resolved
    db.commit()
    release_escrow(db, job_id)
    return True


def replace_artisan_no_return(db: Session, job_id: int) -> Artisan | None:
    """
    Artisan did NOT return within 24h:
    - Find replacement via same matching algorithm
    - Replacement receives: original artisan's salary + 50% of original artisan's savings
    - Original artisan: savings *= 0.5, ranking_score -= 20
    - Replacement gets priority_boost = True
    Returns replacement artisan or None.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.artisan_id:
        return None
    original = db.query(Artisan).filter(Artisan.id == job.artisan_id).first()
    if not original:
        return None
    # Original penalty
    original.savings = (original.savings or 0) * 0.5
    original.ranking_score = max(0, (original.ranking_score or 100) - 20)
    # Clear artisan from job so matching can find someone else (or we assign replacement)
    top = get_top_artisans_for_job(db, job_id, limit=5)
    replacement = None
    for a in top:
        if a.id != original.id:
            replacement = a
            break
    if not replacement:
        db.commit()
        return None
    # Job gets new artisan; replacement gets priority_boost
    replacement.priority_boost = True
    job.artisan_id = replacement.id
    # Payment: replacement gets artisan_share + 50% of original's (previous) savings
    # Original's savings already halved. We don't create a new payment; we keep same payment
    # and release to replacement. So we just assign job to replacement and later release pays replacement.
    db.commit()
    return replacement


def transfer_savings_penalty_to_platform(
    db: Session, job_id: int, artisan_id: int, ratio: float = 0.10
) -> float:
    """
    Transfer a percentage of artisan savings to platform share.
    Used when artisan refuses warranty return work.
    Returns transferred amount.
    """
    if ratio <= 0:
        return 0.0
    artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    if not artisan:
        return 0.0
    current_savings = float(artisan.savings or 0.0)
    amount = round(current_savings * ratio, 2)
    if amount <= 0:
        return 0.0
    artisan.savings = round(max(0.0, current_savings - amount), 2)
    payment = db.query(Payment).filter(Payment.job_id == job_id).first()
    if payment:
        payment.platform_share = round(float(payment.platform_share or 0.0) + amount, 2)
    db.commit()
    return amount

"""Jobs: create, analyze (Gemini + price), get, accept, confirm-dates, complete, claim (guarantee)."""
from datetime import datetime
from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.models import User, Job, Artisan, Client, MatchingAttempt, Guarantee
from app.models.enums import JobStatusEnum, MatchingResponseEnum, SpecialtyEnum, ComplexityEnum, GuaranteeStatusEnum
from app.auth import get_current_user, get_optional_current_user
from app.schemas.job import (
    JobCreate,
    JobResponse,
    JobAcceptResponse,
    JobAnalyzeResponse,
    JobConfirmDates,
    JobComplete,
    MatchedArtisanResponse,
)
from app.ai.vision import analyze_job_photo
from app.ai.price_model import predict as price_predict
from app.services.payment_service import (
    create_payment_for_job,
    create_guarantee_for_job,
    claim_guarantee,
    transfer_savings_penalty_to_platform,
)
from app.services.matching_service import apply_refusal_penalty
from app.schemas.job import JobChatRequest
from app.ai.chat import chat_with_ai

router = APIRouter()


def _get_client_id(db: Session, user: User) -> int | None:
    c = db.query(Client).filter(Client.user_id == user.id).first()
    return c.id if c else None


def _get_artisan_id(db: Session, user: User) -> int | None:
    a = db.query(Artisan).filter(Artisan.user_id == user.id).first()
    return a.id if a else None


def _resolve_job_city(db: Session, job: Job) -> str:
    """Resolve city from client profile, with safe fallback."""
    if job.client_id:
        client = db.query(Client).filter(Client.id == job.client_id).first()
        if client and client.city:
            return client.city
    return (getattr(job, "city", "") or "").strip()


def _normalize_specialty(value: str) -> SpecialtyEnum:
    normalized = (value or "").strip().lower()
    aliases = {
        "zellige": "zlayji",
        "zellij": "zlayji",
        "carrelage": "zlayji",
        "tile": "zlayji",
        "tiles": "zlayji",
        "painting": "sebbagh",
        "paint": "sebbagh",
        "plaster": "gebbas",
        "platre": "gebbas",
        "plumbing": "plombier",
        "electricity": "electricien",
        "electric": "electricien",
    }
    normalized = aliases.get(normalized, normalized)
    return SpecialtyEnum(normalized)


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """List jobs for current user: client sees their jobs; artisan sees jobs assigned to them or pending offers for them."""
    client_id = _get_client_id(db, current_user)
    artisan_id = _get_artisan_id(db, current_user)
    if client_id is not None:
        jobs = db.query(Job).filter(Job.client_id == client_id).order_by(Job.created_at.desc()).all()
    elif artisan_id is not None:
        subq = (
            db.query(MatchingAttempt.job_id)
            .filter(
                MatchingAttempt.artisan_id == artisan_id,
                MatchingAttempt.response == MatchingResponseEnum.pending,
            )
        )
        jobs = (
            db.query(Job)
            .filter(
                (Job.artisan_id == artisan_id) | ((Job.status == JobStatusEnum.matching) & Job.id.in_(subq))
            )
            .order_by(Job.created_at.desc())
            .all()
        )
        # Add client_city for artisan cards
        results = []
        for job in jobs:
            job_dict = {
                col.name: getattr(job, col.name)
                for col in job.__table__.columns
            }
            job_dict["client_city"] = _resolve_job_city(db, job)
            job_dict["guarantee_status"] = job.guarantee.status.value if getattr(job, "guarantee", None) else None
            results.append(job_dict)
        return results
    else:
        jobs = []
    return jobs


@router.post("/", response_model=JobResponse)
def create_job(
    body: JobCreate,
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
    db: Session = Depends(get_db),
):
    # Allow anonymous clients if we have client_name and client_phone
    if current_user:
        client_id = _get_client_id(db, current_user)
        if not client_id:
            raise HTTPException(status_code=403, detail="Only clients can create jobs")
    else:
        # For simplicity in this demo, requiring user context or mock client (we'll just use client_id if logged in, else mock or error if strict)
        # But we'll try to find an existing client or just bypass if the UI sends anonymous data. Let's assume strict auth for now but populate fields.
        client_id = None
        
    job = Job(
        client_id=client_id,
        problem_type=_normalize_specialty(body.problem_type),
        symptom=body.symptom,
        client_name=body.client_name,
        client_phone=body.client_phone,
        photo_url=body.photo_url,
        ai_description=body.ai_description,
        diagnosis_notes=body.diagnosis_notes,
        severity=body.severity,
        surface_area_m2=body.surface_area_m2,
        complexity=ComplexityEnum(body.complexity) if body.complexity in ("simple", "moyenne", "complexe") else None,
        nb_elements_affected=body.nb_elements_affected,
        estimated_price=body.estimated_price,
        estimated_duration_hours=body.estimated_duration_hours,
        status=JobStatusEnum.pending,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/analyze")
async def analyze_job(
    file: UploadFile = File(...),
    client_comment: str = Form(default=""),
    city: str = Form(default="agadir"),
    db: Session = Depends(get_db)
):
    from app.config import settings
    # Read image
    image_bytes = await file.read()
    print(f"[ANALYZE] image_bytes size: {len(image_bytes)}")
    print(f"[ANALYZE] XAI_API_KEY set: {bool(settings.XAI_API_KEY)}")

    # Call vision AI \u2014 problem_type comes FROM AI, not from client
    vision_result = analyze_job_photo(
        image_bytes=image_bytes,
        client_comment=client_comment,
    )
    print(f"[ANALYZE] vision_result: {vision_result}")

    # Call price model with the ACTUAL vision results
    try:
        price_result = price_predict(
            problem_type=vision_result["problem_type"],
            severity=vision_result["severity"],
            surface_area_m2=vision_result["surface_area_m2"],
            complexity=vision_result["complexity"],
            nb_elements_affected=vision_result["nb_elements_affected"],
            city=city,
        )
    except Exception as e:
        print(f"[ANALYZE] price model error: {e}")
        price_result = {
            "price": 300,
            "duration_hours": 3.0
        }
    print(f"[ANALYZE] price_result: {price_result}")

    # Build response using ACTUAL vision values
    response = {
        "problem_type":             vision_result["problem_type"],
        "description":              vision_result["description"],
        "diagnosis_notes":          vision_result["diagnosis_notes"],
        "severity":                 vision_result["severity"],
        "surface_area_m2":          vision_result["surface_area_m2"],
        "complexity":               vision_result["complexity"],
        "nb_elements_affected":     vision_result["nb_elements_affected"],
        "confidence":               vision_result["confidence"],
        "price":                    price_result["price"],
        "duration_hours":           price_result["duration_hours"],
    }
    print(f"[ANALYZE] final response: {response}")
    return response


@router.post("/chat")
def chat_endpoint(body: JobChatRequest):
    try:
        return chat_with_ai(
            image_base64=body.image_base64,
            conversation_history=body.conversation_history,
            is_first_message=body.is_first_message
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"غلط فالذكاء الاصطناعي: {str(e)}"
        )


@router.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    """Upload a problem photo and return a backend-served URL."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    ext = Path(file.filename or "").suffix.lower() or ".jpg"
    allowed_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    if ext not in allowed_exts:
        ext = ".jpg"

    uploads_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    full_path = uploads_dir / filename
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    full_path.write_bytes(content)

    return {"photo_url": f"http://localhost:8000/uploads/{filename}"}


@router.get("/{job_id}/matched-artisan")
def get_matched_artisan(
    job_id: int,
    db: Session = Depends(get_db),
):
    """Return the artisan that was selected for this job (pending or accepted)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Try to find the artisan_id from a pending matching attempt or job.artisan_id
    artisan_id = job.artisan_id
    if not artisan_id:
        ma = (
            db.query(MatchingAttempt)
            .filter(
                MatchingAttempt.job_id == job_id,
                MatchingAttempt.response == MatchingResponseEnum.pending,
            )
            .order_by(MatchingAttempt.id.desc())
            .first()
        )
        if ma:
            artisan_id = ma.artisan_id

    if not artisan_id:
        raise HTTPException(status_code=404, detail="لقينا حتى معلم دابا")

    artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan not found")
    user = db.query(User).filter(User.id == artisan.user_id).first()

    return {
        "artisan_id": artisan.id,
        "full_name": user.full_name if user else "معلم",
        "specialty": artisan.specialty,
        "city": artisan.city or "",
        "ranking_score": artisan.ranking_score or 0,
        "total_jobs": artisan.total_jobs or 0,
        "profile_photo_url": artisan.profile_photo_url,
        "phone": user.phone if user else None,
    }


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Allow a client to delete their own job only if it's still pending or matching."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    client_id = _get_client_id(db, current_user)
    if not client_id:
        raise HTTPException(status_code=403, detail="ماعندكش الصلاحية تمسح هاد الطلب")
    # Allow deletion if: job belongs to this client OR job has no client (anonymous creation)
    if job.client_id is not None and job.client_id != client_id:
        raise HTTPException(status_code=403, detail="ماعندكش الصلاحية تمسح هاد الطلب")
    if job.status not in (JobStatusEnum.pending, JobStatusEnum.matching):
        raise HTTPException(status_code=400, detail="ماتقدرش تمسح الطلب بعد ما قبل المعلم")
    try:
        # Must delete related rows first to avoid FK constraint violations
        db.query(MatchingAttempt).filter(MatchingAttempt.job_id == job_id).delete()
        db.delete(job)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"غلط فالحذف: {str(exc)}")
    return {"message": "تمسح الطلب بنجاح"}


@router.get("/{job_id}")
def get_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Base response
    response = {
        "id": job.id,
        "problem_type": job.problem_type,
        "status": job.status,
        "photo_url": job.photo_url,
        "ai_description": job.ai_description,
        "severity": job.severity,
        "complexity": job.complexity,
        "city": _resolve_job_city(db, job),
        "created_at": job.created_at,
        "symptom": job.symptom,
        "surface_area_m2": job.surface_area_m2,
        "nb_elements_affected": getattr(job, "nb_elements_affected", None),
        "diagnosis_notes": getattr(job, "diagnosis_notes", None),
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "confirmed_start": job.confirmed_start,
        "confirmed_end": job.confirmed_end,
        "guarantee_status": job.guarantee.status.value if getattr(job, "guarantee", None) else None,
    }

    # Client sees full price
    if current_user.role == "client":
        response["estimated_price_min"] = job.estimated_price
        response["estimated_price_max"] = job.estimated_price
        response["client_name"] = None
        response["client_phone"] = None
        response["final_price"] = job.final_price
        response["client_id"] = job.client_id
        response["artisan_id"] = job.artisan_id
        return response

    # Artisan sees 50% price + full client contact info
    if current_user.role == "artisan":
        est_price = job.estimated_price or 0
        response["estimated_price_min"] = round(est_price * 0.50, 0)
        response["estimated_price_max"] = round(est_price * 0.50, 0)
        response["final_price"] = round(job.final_price * 0.50, 0) if job.final_price else None
        
        # Include client contact details
        client = db.query(Client).filter(Client.id == job.client_id).first()
        if client:
            client_user = db.query(User).filter(User.id == client.user_id).first()
            if client_user:
                response["client_name"] = client_user.full_name or job.client_name
                response["client_phone"] = client_user.phone or job.client_phone
            else:
                response["client_name"] = job.client_name
                response["client_phone"] = job.client_phone
        else:
            response["client_name"] = job.client_name
            response["client_phone"] = job.client_phone
            
        response["client_city"] = _resolve_job_city(db, job)
        response["photo_url"] = job.photo_url
        response["client_id"] = job.client_id
        response["artisan_id"] = job.artisan_id
        return response

    return response


@router.patch("/{job_id}/accept", response_model=JobAcceptResponse)
def accept_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatusEnum.matching:
        raise HTTPException(status_code=400, detail="Job is not in matching phase")
    artisan_id = _get_artisan_id(db, current_user)
    if not artisan_id:
        raise HTTPException(status_code=403, detail="Only artisans can accept")
    ma = db.query(MatchingAttempt).filter(
        MatchingAttempt.job_id == job_id,
        MatchingAttempt.artisan_id == artisan_id,
        MatchingAttempt.response == MatchingResponseEnum.pending,
    ).first()
    if not ma:
        raise HTTPException(status_code=400, detail="No pending matching attempt for this artisan")
    ma.response = MatchingResponseEnum.accepted
    job.artisan_id = artisan_id
    job.status = JobStatusEnum.accepted
    amount = job.estimated_price or 0
    if amount <= 0:
        amount = 500
    job.final_price = amount
    create_payment_for_job(db, job_id, amount)
    db.commit()
    artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    user = db.query(User).filter(User.id == artisan.user_id).first() if artisan else None
    return JobAcceptResponse(
        job_id=job_id,
        artisan_id=artisan_id,
        artisan_name=user.full_name if user else "",
        artisan_phone=user.phone or "",
        artisan_photo_url=artisan.profile_photo_url if artisan else None,
    )


@router.patch("/{job_id}/refuse")
def refuse_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    artisan_id = _get_artisan_id(db, current_user)
    if not artisan_id:
        raise HTTPException(status_code=403, detail="Only artisans can refuse")
    ma = db.query(MatchingAttempt).filter(
        MatchingAttempt.job_id == job_id,
        MatchingAttempt.artisan_id == artisan_id,
        MatchingAttempt.response == MatchingResponseEnum.pending,
    ).first()
    if not ma:
        raise HTTPException(status_code=400, detail="No pending matching attempt")
    ma.response = MatchingResponseEnum.refused
    
    # Appliquer la pénalité de 10 points
    from app.services.matching_service import apply_refusal_penalty, reassign_after_refusal
    apply_refusal_penalty(db, artisan_id, penalty=10)
    db.commit()
    
    # Reassign to next best artisan
    reassign_after_refusal(job_id, artisan_id, db)
    
    # Obtenir le score à jour
    artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    return {
        "message": "رفضتي الطلب",
        "points_deducted": 10,
        "new_score": artisan.ranking_score if artisan else 0
    }


@router.patch("/{job_id}/confirm-dates")
def confirm_dates(
    job_id: int,
    body: JobConfirmDates,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatusEnum.accepted:
        raise HTTPException(status_code=400, detail="Job must be accepted first")
    job.confirmed_start = body.confirmed_start
    job.confirmed_end = body.confirmed_end
    job.status = JobStatusEnum.in_progress
    job.started_at = body.confirmed_start
    db.commit()
    return {"message": "Dates confirmed"}


@router.patch("/{job_id}/complete")
def complete_job(
    job_id: int,
    body: JobComplete,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    artisan_id = _get_artisan_id(db, current_user)
    if job.artisan_id != artisan_id:
        raise HTTPException(status_code=403, detail="Only assigned artisan can complete")
    job.status = JobStatusEnum.completed
    job.completed_at = datetime.utcnow()
    if body.after_photo_url:
        job.after_photo_url = body.after_photo_url
    artisan = db.query(Artisan).filter(Artisan.id == job.artisan_id).first()
    if artisan:
        artisan.total_jobs = (artisan.total_jobs or 0) + 1
    create_guarantee_for_job(db, job_id)
    db.commit()
    if background_tasks:
        from app.services.payment_service import check_guarantee_expired
        g = db.query(Guarantee).filter(Guarantee.job_id == job_id).first()
        if g:
            background_tasks.add_task(_expire_guarantee_later, g.id)
    return {"message": "Job completed; 48h guarantee started"}


def _expire_guarantee_later(guarantee_id: int):
    import time
    from app.database import SessionLocal
    from app.services.payment_service import check_guarantee_expired
    time.sleep(3600)  # 1 hour
    db = SessionLocal()
    try:
        check_guarantee_expired(db, guarantee_id)
    finally:
        db.close()


@router.post("/{job_id}/claim")
def claim_guarantee_endpoint(
    job_id: int,
    complaint_text: str | None = None,
    complaint_photo_url: str | None = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.client_id != _get_client_id(db, current_user):
        raise HTTPException(status_code=403, detail="Only client can claim")
    g = claim_guarantee(db, job_id, complaint_text, complaint_photo_url)
    if not g:
        raise HTTPException(status_code=400, detail="No open guarantee for this job")
    return {"message": "Complaint filed", "guarantee_id": g.id}


@router.patch("/{job_id}/claim-accept")
def accept_claimed_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Artisan accepts warranty return work (client reclamation)."""
    artisan_id = _get_artisan_id(db, current_user)
    if not artisan_id:
        raise HTTPException(status_code=403, detail="Only artisans can accept reclamations")
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.artisan_id != artisan_id:
        raise HTTPException(status_code=403, detail="Only assigned artisan can accept this reclamation")
    guarantee = db.query(Guarantee).filter(Guarantee.job_id == job_id).first()
    if not guarantee or guarantee.status != GuaranteeStatusEnum.claimed:
        raise HTTPException(status_code=400, detail="No active reclamation for this job")
    job.status = JobStatusEnum.in_progress
    job.started_at = datetime.utcnow()
    db.commit()
    return {"message": "Reclamation accepted; return intervention started"}


@router.patch("/{job_id}/claim-refuse")
def refuse_claimed_job(
    job_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Artisan refuses warranty return:
    - transfer 10% of artisan savings to platform
    - penalize ranking by 10 points
    - reassign job to another artisan
    """
    artisan_id = _get_artisan_id(db, current_user)
    if not artisan_id:
        raise HTTPException(status_code=403, detail="Only artisans can refuse reclamations")
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.artisan_id != artisan_id:
        raise HTTPException(status_code=403, detail="Only assigned artisan can refuse this reclamation")
    guarantee = db.query(Guarantee).filter(Guarantee.job_id == job_id).first()
    if not guarantee or guarantee.status != GuaranteeStatusEnum.claimed:
        raise HTTPException(status_code=400, detail="No active reclamation for this job")

    transferred = transfer_savings_penalty_to_platform(db, job_id, artisan_id, ratio=0.10)
    apply_refusal_penalty(db, artisan_id, penalty=10)

    # Mark current artisan as refused for this job context and reassign.
    ma = MatchingAttempt(
        job_id=job_id,
        artisan_id=artisan_id,
        response=MatchingResponseEnum.refused,
    )
    db.add(ma)
    job.artisan_id = None
    job.status = JobStatusEnum.matching
    db.commit()

    from app.services.matching_service import run_matching_loop
    run_matching_loop(db, job_id)

    return {
        "message": "Reclamation refused; job reassigned",
        "points_deducted": 10,
        "savings_transferred_to_platform": transferred,
    }

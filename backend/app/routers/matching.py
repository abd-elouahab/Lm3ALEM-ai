"""POST /match — trigger matching algorithm as background task."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models import Job
from app.models.enums import JobStatusEnum
from app.auth import get_optional_current_user
from app.models import User
from app.routers.jobs import _get_client_id

router = APIRouter()


def _run_matching_task(job_id: int) -> None:
    from app.services.matching_service import run_matching_loop
    db = SessionLocal()
    try:
        run_matching_loop(db, job_id)
    finally:
        db.close()


@router.post("/")
def trigger_match(
    body: dict = Body(...),
    background_tasks: BackgroundTasks = None,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    job_id = body.get("job_id")
    if job_id is None:
        raise HTTPException(status_code=400, detail="job_id required")
    job_id = int(job_id)
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.client_id is not None:
        if current_user is None or job.client_id != _get_client_id(db, current_user):
            raise HTTPException(status_code=403, detail="Only job client can trigger matching")
            
    if job.status != JobStatusEnum.pending:
        raise HTTPException(status_code=400, detail="Job must be in pending status")
    job.status = JobStatusEnum.matching
    db.commit()
    background_tasks.add_task(_run_matching_task, job_id)
    return {"message": "Matching started", "job_id": job_id}

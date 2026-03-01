"""Job Pydantic schemas."""
from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class JobCreate(BaseModel):
    problem_type: Literal["zlayji", "sebbagh", "gebbas", "plombier", "electricien"]
    symptom: str | None = None
    client_name: str | None = None
    client_phone: str | None = None
    photo_url: str | None = None
    city: str | None = None
    client_latitude: float | None = None
    client_longitude: float | None = None
    ai_description: str | None = None
    diagnosis_notes: str | None = None
    severity: int | None = None
    surface_area_m2: float | None = None
    complexity: str | None = None
    nb_elements_affected: int | None = None
    estimated_price: float | None = None
    estimated_duration_hours: float | None = None

class JobChatRequest(BaseModel):
    image_base64: str
    conversation_history: list[dict]
    is_first_message: bool


class JobResponse(BaseModel):
    id: int
    client_id: int | None
    artisan_id: int | None
    client_name: str | None = None
    client_phone: str | None = None
    problem_type: str
    symptom: str | None
    photo_url: str | None
    ai_description: str | None
    diagnosis_notes: str | None = None
    severity: int | None
    surface_area_m2: float | None
    complexity: str | None
    nb_elements_affected: int | None
    estimated_price: float | None
    estimated_duration_hours: float | None
    final_price: float | None
    city: str | None = None
    client_city: str | None = None
    guarantee_status: str | None = None
    status: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    confirmed_start: datetime | None
    confirmed_end: datetime | None

    class Config:
        from_attributes = True


class JobAcceptResponse(BaseModel):
    job_id: int
    artisan_id: int
    artisan_name: str
    artisan_phone: str
    artisan_photo_url: str | None


class MatchedArtisanResponse(BaseModel):
    artisan_id: int
    full_name: str
    specialty: str
    city: str
    ranking_score: float
    total_jobs: int
    profile_photo_url: str | None
    phone: str | None


class JobAnalyzeResponse(BaseModel):
    problem_type: str
    description: str
    diagnosis_notes: str | None = None
    severity: int
    surface_area_m2: float
    complexity: str
    nb_elements_affected: int
    confidence: str
    price: float
    duration_hours: float


class JobConfirmDates(BaseModel):
    confirmed_start: datetime
    confirmed_end: datetime


class JobComplete(BaseModel):
    after_photo_url: str | None = None

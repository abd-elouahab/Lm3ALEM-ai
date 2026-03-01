"""Artisan Pydantic schemas."""
from pydantic import BaseModel
from datetime import datetime


class ArtisanResponse(BaseModel):
    id: int
    user_id: int
    specialty: str
    city: str
    latitude: float
    longitude: float
    is_available: bool
    ranking_score: float
    savings: float
    total_jobs: int
    bio: str | None
    profile_photo_url: str | None
    full_name: str | None = None
    phone: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ArtisanListResponse(BaseModel):
    id: int
    specialty: str
    city: str
    is_available: bool
    ranking_score: float
    total_jobs: int
    full_name: str | None = None
    profile_photo_url: str | None = None

    class Config:
        from_attributes = True


class ArtisanAvailability(BaseModel):
    is_available: bool

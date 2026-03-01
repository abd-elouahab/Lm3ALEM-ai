"""Artisans: list (with filters), get profile, PATCH availability."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.models import Artisan, User
from app.auth import get_current_user
from app.schemas.artisan import ArtisanResponse, ArtisanListResponse, ArtisanAvailability

router = APIRouter()


@router.get("/", response_model=list[ArtisanListResponse])
def list_artisans(
    db: Session = Depends(get_db),
    specialty: str | None = Query(None),
    city: str | None = Query(None),
    is_available: bool | None = Query(None),
):
    q = db.query(Artisan)
    if specialty:
        try:
            from app.models.enums import SpecialtyEnum
            q = q.filter(Artisan.specialty == SpecialtyEnum(specialty))
        except ValueError:
            pass
    if city:
        q = q.filter(Artisan.city.ilike(f"%{city}%"))
    if is_available is not None:
        q = q.filter(Artisan.is_available == is_available)
    artisans = q.all()
    out = []
    for a in artisans:
        user = db.query(User).filter(User.id == a.user_id).first()
        out.append(ArtisanListResponse(
            id=a.id,
            specialty=a.specialty.value,
            city=a.city,
            is_available=a.is_available,
            ranking_score=a.ranking_score,
            total_jobs=a.total_jobs,
            full_name=user.full_name if user else None,
            profile_photo_url=a.profile_photo_url,
        ))
    return out


@router.get("/me", response_model=ArtisanResponse)
def get_my_artisan_profile(
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    a = db.query(Artisan).filter(Artisan.user_id == current_user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Artisan profile not found")
    user = db.query(User).filter(User.id == a.user_id).first()
    return ArtisanResponse(
        id=a.id,
        user_id=a.user_id,
        specialty=a.specialty.value,
        city=a.city,
        latitude=a.latitude,
        longitude=a.longitude,
        is_available=a.is_available,
        ranking_score=a.ranking_score,
        savings=a.savings,
        total_jobs=a.total_jobs,
        bio=a.bio,
        profile_photo_url=a.profile_photo_url,
        full_name=user.full_name if user else None,
        phone=user.phone if user else None,
        created_at=a.created_at,
    )


@router.get("/{artisan_id}", response_model=ArtisanResponse)
def get_artisan(
    artisan_id: int,
    db: Session = Depends(get_db),
):
    a = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Artisan not found")
    user = db.query(User).filter(User.id == a.user_id).first()
    return ArtisanResponse(
        id=a.id,
        user_id=a.user_id,
        specialty=a.specialty.value,
        city=a.city,
        latitude=a.latitude,
        longitude=a.longitude,
        is_available=a.is_available,
        ranking_score=a.ranking_score,
        savings=a.savings,
        total_jobs=a.total_jobs,
        bio=a.bio,
        profile_photo_url=a.profile_photo_url,
        full_name=user.full_name if user else None,
        phone=user.phone if user else None,
        created_at=a.created_at,
    )


@router.patch("/{artisan_id}/availability")
def set_availability(
    artisan_id: int,
    body: ArtisanAvailability,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Session = Depends(get_db),
):
    a = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Artisan not found")
    if a.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only own profile")
    a.is_available = body.is_available
    db.commit()
    return {"is_available": a.is_available}

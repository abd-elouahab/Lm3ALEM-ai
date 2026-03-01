"""Auth: register (client/artisan), login (JWT)."""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Artisan, Client
from app.models.enums import UserRole, SpecialtyEnum
from app.auth import get_password_hash, create_access_token, verify_password, get_current_user
from app.schemas.auth import UserCreate, UserResponse, Token

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=body.email,
        password_hash=get_password_hash(body.password),
        role=UserRole(body.role),
        full_name=body.full_name,
        phone=body.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    if body.role == "artisan":
        if not all([body.specialty, body.city is not None, body.latitude is not None, body.longitude is not None]):
            raise HTTPException(status_code=400, detail="Artisan must provide specialty, city, latitude, longitude")
        artisan = Artisan(
            user_id=user.id,
            specialty=SpecialtyEnum(body.specialty),
            city=body.city,
            latitude=float(body.latitude),
            longitude=float(body.longitude),
            bio=body.bio,
            profile_photo_url=body.profile_photo_url,
        )
        db.add(artisan)
    else:
        if not all([body.client_city, body.client_latitude is not None, body.client_longitude is not None]):
            raise HTTPException(status_code=400, detail="Client must provide client_city, client_latitude, client_longitude")
        client = Client(
            user_id=user.id,
            city=body.client_city,
            latitude=float(body.client_latitude),
            longitude=float(body.client_longitude),
        )
        db.add(client)
    db.commit()
    return user


@router.post("/login", response_model=Token)
def login(
    username: str = Form(..., description="Email"),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role.value})
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user

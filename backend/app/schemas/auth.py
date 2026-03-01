"""Auth Pydantic schemas."""
from pydantic import BaseModel, EmailStr
from typing import Literal


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Literal["client", "artisan"]
    full_name: str
    phone: str | None = None
    # For artisan
    specialty: Literal["zlayji", "sebbagh", "gebbas", "plombier", "electricien"] | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    bio: str | None = None
    profile_photo_url: str | None = None
    # For client
    client_city: str | None = None
    client_latitude: float | None = None
    client_longitude: float | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    full_name: str
    phone: str | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None
    role: str | None = None

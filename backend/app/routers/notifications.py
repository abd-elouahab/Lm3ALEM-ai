"""Internal: POST /notify — send SMS via Twilio."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.notification_service import send_sms

router = APIRouter()


class NotifyBody(BaseModel):
    phone: str
    message: str


@router.post("/")
def notify(body: NotifyBody):
    ok = send_sms(body.phone, body.message)
    if not ok:
        raise HTTPException(status_code=500, detail="SMS send failed")
    return {"sent": True}

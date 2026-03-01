"""Send SMS via Twilio."""
from sqlalchemy.orm import Session
from twilio.rest import Client as TwilioClient
from app.config import settings
from app.models import Artisan, User


def send_sms_to_artisan(db: Session, artisan_id: int, job_id: int) -> bool:
    """Send SMS to artisan's phone (from User) for job match notification."""
    artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
    if not artisan:
        return False
    user = db.query(User).filter(User.id == artisan.user_id).first()
    if not user or not user.phone:
        return False
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
        return False
    try:
        client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        body = f"L'M3alem AI: Vous avez une nouvelle mission #{job_id}. Répondez pour accepter."
        client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone,
        )
        return True
    except Exception:
        return False


def send_sms(phone: str, message: str) -> bool:
    """Generic SMS send."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
        return False
    try:
        client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )
        return True
    except Exception:
        return False

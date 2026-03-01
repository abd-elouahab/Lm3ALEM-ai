"""Application configuration from environment."""
import os
from pathlib import Path

# Force-load backend/.env so it overrides system env (e.g. DATABASE_URL)
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"
if _ENV_FILE.exists():
    from dotenv import load_dotenv
    load_dotenv(_ENV_FILE, override=True)
    # Ensure DATABASE_URL from file wins (Windows/env edge cases)
    from dotenv import dotenv_values
    file_vars = dotenv_values(_ENV_FILE)
    if "DATABASE_URL" in file_vars and file_vars["DATABASE_URL"]:
        os.environ["DATABASE_URL"] = file_vars["DATABASE_URL"]

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "L'M3alem AI"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://postgres:abdoABDO20202020@localhost:5432/lm3alem_ai"
    GOOGLE_GEMINI_API_KEY: str = ""
    XAI_API_KEY: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    JWT_SECRET: str = "change-me-in-production"
    JWT_EXPIRE_MINUTES: int = 1440
    JWT_ALGORITHM: str = "HS256"
    MATCHING_WAIT_MINUTES: int = 30
    GUARANTEE_HOURS: int = 48

    class Config:
        env_file = str(_ENV_FILE) if _ENV_FILE.exists() else None
        extra = "ignore"


settings = Settings()

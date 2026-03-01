"""Database connection and session — PostgreSQL."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Prefer DATABASE_URL from backend/.env so it always wins over system env
_backend_dir = Path(__file__).resolve().parent.parent
_env_file = _backend_dir / ".env"
_database_url = None
if _env_file.exists():
    from dotenv import dotenv_values
    _vars = dotenv_values(_env_file)
    if _vars.get("DATABASE_URL"):
        _database_url = _vars["DATABASE_URL"]

if _database_url is None:
    from app.config import settings
    _database_url = settings.DATABASE_URL

engine = create_engine(
    _database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

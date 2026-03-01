"""L'M3alem AI — Application entry point."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.routers import auth, jobs, matching, artisans, ratings, notifications

# Import models so they register with Base.metadata before create_all
from app import models  # noqa: F401

app = FastAPI(title=settings.APP_NAME)

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_UPLOADS_DIR = _BACKEND_DIR / "uploads"
_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
def on_startup():
    """Create database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(matching.router, prefix="/match", tags=["matching"])
app.include_router(artisans.router, prefix="/artisans", tags=["artisans"])
app.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
app.include_router(notifications.router, prefix="/notify", tags=["notifications"])
app.mount("/uploads", StaticFiles(directory=str(_UPLOADS_DIR)), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch any unhandled exception and return a proper JSON response.
    Without this, FastAPI drops the TCP connection, which strips CORS headers."""
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error": "Internal Server Error"},
    )

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routers import router as api_router


def _seed_demo_users() -> None:
    """Create the 5 SIH demo persona accounts in the DB if they don't exist yet."""
    from app.core.database import SessionLocal
    from app.core.security import get_password_hash
    from app.models.database_models import UserDB

    DEMO_ACCOUNTS = [
        {"username": "fisherman",  "email": "fisherman@varuna.gov.in",  "role": "Fisherman",  "full_name": "Demo Fisherman"},
        {"username": "shipping",   "email": "shipping@varuna.gov.in",   "role": "Shipping",   "full_name": "Demo Shipping Captain"},
        {"username": "disaster",   "email": "disaster@varuna.gov.in",   "role": "Disaster",   "full_name": "Demo Disaster Commander"},
        {"username": "researcher", "email": "researcher@varuna.gov.in", "role": "Researcher", "full_name": "Demo Marine Researcher"},
        {"username": "admin",      "email": "admin@varuna.gov.in",      "role": "Admin",      "full_name": "Demo System Admin"},
    ]
    DEMO_PASSWORD = "demo123"

    db = SessionLocal()
    try:
        for account in DEMO_ACCOUNTS:
            existing = db.query(UserDB).filter(UserDB.username == account["username"]).first()
            if not existing:
                db.add(UserDB(
                    username=account["username"],
                    email=account["email"],
                    hashed_password=get_password_hash(DEMO_PASSWORD),
                    role=account["role"],
                    full_name=account["full_name"],
                    is_active=True,
                ))
        db.commit()
        print("[VARUNA] Demo user accounts seeded ✓")
    except Exception as e:
        print(f"[VARUNA] Demo seeding warning: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    _seed_demo_users()
    yield
    # ── Shutdown (nothing to clean up yet) ───────────────────────────────────


app = FastAPI(
    title=settings.PROJECT_TITLE,
    description=f"VARUNA - Agentic AI-Powered Marine Intelligence Platform for SIH 2026. Tagline: {settings.TAGLINE}",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static reports directory exists and mount static files
reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "reports"))
os.makedirs(reports_dir, exist_ok=True)
app.mount("/static/reports", StaticFiles(directory=reports_dir), name="static_reports")

# Include main API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "title": settings.PROJECT_TITLE,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "RUNNING",
        "docs": "/docs",
        "target": "Smart India Hackathon (SIH) 2026"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


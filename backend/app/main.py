from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from . import models  # noqa: F401
from .sports.registry import build_default_registry
from .api.routes import router as api_router

app = FastAPI(title=settings.app_name, version="0.2.0")
app.include_router(api_router)
sport_registry = build_default_registry()


@app.on_event("startup")
def create_legacy_core_tables() -> None:
    # Existing Phase 0/1 core tables remain bootstrapped here for backwards compatibility.
    # New sport-specific tables are managed by Alembic: cd backend && alembic upgrade head.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "environment": settings.app_env, "database": "ok"}


@app.get("/")
def root():
    return {"name": settings.app_name, "version": "0.2.0", "status": "running"}


@app.get("/api/v1/meta")
def meta():
    return {
        "sports": [
            {"code": sport.code, "name": sport.display_name}
            for sport in sport_registry.list()
        ],
        "phase": "multi-sport data and baseline APIs",
        "purpose": "private local research and validation",
    }

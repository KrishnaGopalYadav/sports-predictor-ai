from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from . import models  # noqa: F401

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.on_event("startup")
def create_tables() -> None:
    # Temporary Phase 0/1 bootstrap. Alembic migrations will replace this before R1.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "environment": settings.app_env, "database": "ok"}


@app.get("/")
def root():
    return {"name": settings.app_name, "version": "0.1.0", "status": "running"}


@app.get("/api/v1/meta")
def meta():
    return {
        "sports": ["cricket", "football"],
        "phase": "R1 foundation",
        "purpose": "private local research and validation",
    }

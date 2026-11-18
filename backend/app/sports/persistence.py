"""Provider-scoped external identity helpers.

External IDs are not globally unique. Always scope them by provider, sport and entity type.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.sports.models import ExternalIdentity


def find_internal_id(db: Session, *, provider: str, sport: str, entity_type: str, external_id: str):
    row = db.scalar(select(ExternalIdentity).where(
        ExternalIdentity.provider == provider,
        ExternalIdentity.sport == sport,
        ExternalIdentity.entity_type == entity_type,
        ExternalIdentity.external_id == str(external_id),
    ))
    return row.internal_id if row else None


def record_identity(db: Session, *, provider: str, sport: str, entity_type: str,
                    external_id: str, internal_id: int) -> ExternalIdentity:
    existing = db.scalar(select(ExternalIdentity).where(
        ExternalIdentity.provider == provider,
        ExternalIdentity.sport == sport,
        ExternalIdentity.entity_type == entity_type,
        ExternalIdentity.external_id == str(external_id),
    ))
    if existing:
        if existing.internal_id != internal_id:
            raise ValueError("provider identity already maps to a different internal entity")
        return existing
    row = ExternalIdentity(provider=provider, sport=sport, entity_type=entity_type,
                           external_id=str(external_id), internal_id=internal_id)
    db.add(row)
    db.flush()
    return row

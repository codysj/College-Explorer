from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.event import Event


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_event(
        self,
        user_id: int | None,
        event_name: str,
        entity_type: str | None,
        entity_id: int | None,
        metadata: dict[str, object],
    ) -> dict[str, object]:
        event = Event(
            user_id=user_id,
            event_name=event_name,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_=metadata,
        )
        self.db.add(event)
        self.db.flush()
        self.db.commit()
        return event_row(event)

    def list_events(self, lookback_days: int = 90, limit: int = 5000) -> list[dict[str, object]]:
        since = datetime.now(UTC) - timedelta(days=lookback_days)
        query = (
            select(Event)
            .where(Event.created_at >= since)
            .order_by(Event.created_at.desc(), Event.id.desc())
            .limit(limit)
        )
        return [event_row(event) for event in self.db.scalars(query).all()]


def event_row(event: Event) -> dict[str, object]:
    return {
        "id": int(event.id),
        "user_id": event.user_id,
        "event_name": event.event_name,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "metadata": event.metadata_ or {},
        "created_at": event.created_at,
    }

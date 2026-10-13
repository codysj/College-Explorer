from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.event import Event


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_events(self, events: list[dict[str, object]]) -> list[dict[str, object]]:
        """Insert events in one transaction. On failure the session is rolled back, so the
        request's other queries are not left running on an aborted transaction."""
        rows = [
            Event(
                event_name=event["event_name"],
                entity_type=event["entity_type"],
                entity_id=event["entity_id"],
                metadata_=event["metadata"],
            )
            for event in events
        ]
        try:
            self.db.add_all(rows)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return [event_row(row) for row in rows]

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

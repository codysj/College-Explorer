from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.deps import get_db
from core.config import Settings, get_settings
from schemas.health import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health",
    description="Returns process-level API health without requiring a database connection.",
)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        version=settings.app_version,
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness check",
    description="Checks whether the API can open a database session and execute a lightweight query.",
)
def ready(db: Session = Depends(get_db)) -> ReadyResponse:
    db.execute(text("SELECT 1"))
    return ReadyResponse(
        status="ready",
        database="ok",
        timestamp=datetime.now(UTC),
    )

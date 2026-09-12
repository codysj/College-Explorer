from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from repositories.analytics import AnalyticsRepository
from schemas.analytics import AnalyticsEventCreate, AnalyticsEventResponse, AnalyticsSummaryResponse
from services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(db))


@router.post(
    "/events",
    response_model=AnalyticsEventResponse,
    summary="Log a privacy-safe analytics event",
)
def log_analytics_event(
    request: AnalyticsEventCreate,
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsEventResponse:
    return service.log_event(request)


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Return internal analytics and ranking evaluation summary",
)
def analytics_summary(
    lookback_days: int = Query(default=90, ge=1, le=365),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsSummaryResponse:
    return service.summary(lookback_days=lookback_days)

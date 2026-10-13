from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from api.routes.analytics import get_analytics_service
from core.rate_limit import RateLimit
from repositories.schools import SchoolRepository
from schemas.analytics import AnalyticsEventCreate
from schemas.decision import DecisionReportRequest, DecisionReportResponse
from services.analytics import AnalyticsService
from services.cache import CacheService
from services.decision import DecisionService
from services.ranking_service import RankingService

router = APIRouter(prefix="/decision", tags=["decision"])


def get_decision_service(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> DecisionService:
    repository = SchoolRepository(db)
    return DecisionService(repository, RankingService(repository, cache))


@router.post(
    "/report",
    response_model=DecisionReportResponse,
    summary="Generate a deterministic accepted-school decision report",
    dependencies=[Depends(RateLimit("decision"))],
)
def build_decision_report(
    request: DecisionReportRequest,
    service: DecisionService = Depends(get_decision_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> DecisionReportResponse:
    try:
        response = service.build_report(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    analytics.try_log_event(
        AnalyticsEventCreate(
            event_name="decision_report_generated",
            entity_type="decision_report",
            metadata={
                "ranking_version": response.ranking_version,
                "report_version": response.report_version,
                "school_count": len(response.schools),
                "decision_confidence": response.decision_confidence,
            },
        )
    )
    return response

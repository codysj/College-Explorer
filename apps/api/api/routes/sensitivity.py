from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from api.routes.analytics import get_analytics_service
from repositories.schools import SchoolRepository
from schemas.analytics import AnalyticsEventCreate
from schemas.sensitivity import SensitivityRequest, SensitivityResponse
from services.analytics import AnalyticsService
from services.cache import CacheService
from services.sensitivity import SensitivityService

router = APIRouter(tags=["sensitivity"])


def get_sensitivity_service(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> SensitivityService:
    return SensitivityService(SchoolRepository(db), cache)


@router.post(
    "/sensitivity",
    response_model=SensitivityResponse,
    summary="Analyze deterministic ranking sensitivity to preference weights",
)
def analyze_sensitivity(
    request: SensitivityRequest,
    service: SensitivityService = Depends(get_sensitivity_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> SensitivityResponse:
    response = service.analyze(request)
    analytics.try_log_event(
        AnalyticsEventCreate(
            event_name="sensitivity_adjusted",
            entity_type="ranking",
            metadata={
                "ranking_version": response.ranking_version,
                "candidate_count": len(request.candidate_school_ids),
                "scenario_count": len(request.scenarios),
                "emphasis_dimension": response.scenarios[0].emphasis_dimension if response.scenarios else None,
                "category_weights": response.baseline_weights,
            },
        )
    )
    return response

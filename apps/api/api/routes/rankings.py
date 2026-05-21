from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from api.routes.analytics import get_analytics_service
from repositories.schools import SchoolRepository
from schemas.analytics import AnalyticsEventCreate
from schemas.rankings import RankingRequest, RankingResponse
from services.analytics import AnalyticsService
from services.cache import CacheService
from services.ranking_service import RankingService

router = APIRouter(prefix="/rankings", tags=["rankings"])


def get_ranking_service(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> RankingService:
    return RankingService(SchoolRepository(db), cache)


@router.post(
    "",
    response_model=RankingResponse,
    summary="Rank schools deterministically",
    description="Returns ranked school search cards using structured preferences and deterministic reason codes.",
)
def rank_schools(
    request: RankingRequest,
    service: RankingService = Depends(get_ranking_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> RankingResponse:
    response = service.rank_schools(request)
    for index, result in enumerate(response.results, start=1):
        analytics.try_log_event(
            AnalyticsEventCreate(
                event_name="ranking_generated",
                entity_type="school",
                entity_id=result.school_id,
                metadata={
                    "ranking_version": response.ranking_version,
                    "ranking_result_count": response.total_results,
                    "rank_position": (response.page - 1) * response.page_size + index,
                    "fit_score": result.fit_score,
                    "confidence_score": result.confidence_score,
                    "top_reasons": result.top_reasons,
                    "top_tradeoffs": result.top_tradeoffs,
                    "category_scores": result.category_scores or {},
                    "category_weights": request.preferences.weights,
                },
            )
        )
    return response

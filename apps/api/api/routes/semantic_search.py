from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from api.routes.analytics import get_analytics_service
from repositories.schools import SchoolRepository
from schemas.analytics import AnalyticsEventCreate
from schemas.semantic_search import SemanticSearchRequest, SemanticSearchResponse
from services.analytics import AnalyticsService
from services.cache import CacheService
from services.semantic_search import SemanticSearchService

router = APIRouter(tags=["semantic-search"])


def get_semantic_search_service(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> SemanticSearchService:
    return SemanticSearchService(SchoolRepository(db), cache)


@router.post(
    "/semantic-search",
    response_model=SemanticSearchResponse,
    summary="Semantic school search",
    description="Retrieves semantic candidates, applies structured constraints, and re-ranks with deterministic scoring.",
)
def semantic_search(
    request: SemanticSearchRequest,
    service: SemanticSearchService = Depends(get_semantic_search_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> SemanticSearchResponse:
    response = service.search(request)
    analytics.try_log_event(
        AnalyticsEventCreate(
            event_name="semantic_search_performed",
            entity_type="search",
            metadata={
                "result_count": response.total_results,
                "page": response.page,
                "page_size": response.page_size,
                "retrieval_mode": response.retrieval_mode,
                "ranking_version": response.ranking_version,
                "filters": request.filters.model_dump(mode="json") if request.filters else {},
                "query_present": True,
                "query_length": len(request.query),
            },
        )
    )
    for index, result in enumerate(response.results, start=1):
        analytics.try_log_event(
            AnalyticsEventCreate(
                event_name="ranking_generated",
                entity_type="school",
                entity_id=result.school_id,
                metadata={
                    "source": "semantic_search",
                    "ranking_version": response.ranking_version,
                    "rank_position": (response.page - 1) * response.page_size + index,
                    "fit_score": result.fit_score,
                    "confidence_score": result.confidence_score,
                    "top_reasons": result.top_reasons,
                    "category_scores": result.category_scores or {},
                    "category_weights": request.preferences.weights if request.preferences else {},
                },
            )
        )
    return response

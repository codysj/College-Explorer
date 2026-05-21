from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from api.routes.analytics import get_analytics_service
from core.logging import get_logger
from repositories.schools import SchoolRepository
from schemas.similar_schools import SimilarSchoolsRequest, SimilarSchoolsResponse
from schemas.schools import SchoolProfileResponse, SearchRequest, SearchResponse
from services.cache import CacheService
from services.analytics import AnalyticsService
from schemas.analytics import AnalyticsEventCreate
from services.similar_schools import SimilarSchoolsService
from services.schools import SchoolService

router = APIRouter(prefix="/schools", tags=["schools"])
logger = get_logger(__name__)


def get_school_service(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> SchoolService:
    return SchoolService(db, cache)


def get_similar_schools_service(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> SimilarSchoolsService:
    return SimilarSchoolsService(SchoolRepository(db), cache)


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Structured school search",
    description="Returns paginated school search cards using structured filters and deterministic sorting.",
)
def search_schools(
    filters: Annotated[SearchRequest, Depends()],
    service: SchoolService = Depends(get_school_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> SearchResponse:
    response = service.search_schools(filters)
    analytics.try_log_event(
        AnalyticsEventCreate(
            event_name="search_performed",
            entity_type="search",
            metadata={
                "result_count": response.total_results,
                "page": response.page,
                "page_size": response.page_size,
                "filters": filters.model_dump(mode="json"),
                "query_present": bool(filters.query),
                "query_length": len(filters.query or ""),
            },
        )
    )
    return response


@router.get(
    "/{school_id}/similar",
    response_model=SimilarSchoolsResponse,
    summary="Similar schools",
    description="Returns explainable similar-school alternatives with deterministic variant logic.",
)
def get_similar_schools(
    school_id: int,
    request: Annotated[SimilarSchoolsRequest, Depends()],
    service: SimilarSchoolsService = Depends(get_similar_schools_service),
) -> SimilarSchoolsResponse:
    response = service.get_similar_schools(school_id, request)
    if response is None:
        raise HTTPException(status_code=404, detail="School not found.")
    return response


@router.get(
    "/{school_id}",
    response_model=SchoolProfileResponse,
    summary="School profile",
    description="Returns a full structured school profile with explicit missing-data metadata.",
)
def get_school_profile(
    school_id: int,
    service: SchoolService = Depends(get_school_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> SchoolProfileResponse:
    profile = service.get_school_profile(school_id)
    if profile is None:
        logger.info(
            "school_profile_not_found",
            extra={
                "request_id": x_request_id,
                "school_id": school_id,
                "failure_reason": "school_id_not_found",
            },
        )
        raise HTTPException(status_code=404, detail="School not found.")
    analytics.try_log_event(
        AnalyticsEventCreate(
            event_name="school_profile_viewed",
            entity_type="school",
            entity_id=school_id,
            metadata={"school_name": profile.name},
        )
    )
    return profile

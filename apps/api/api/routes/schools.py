from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from core.logging import get_logger
from schemas.schools import SchoolProfileResponse, SearchRequest, SearchResponse
from services.schools import SchoolService

router = APIRouter(prefix="/schools", tags=["schools"])
logger = get_logger(__name__)


def get_school_service(db: Session = Depends(get_db)) -> SchoolService:
    return SchoolService(db)


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Structured school search",
    description="Returns paginated school search cards using structured filters and deterministic sorting.",
)
def search_schools(
    filters: Annotated[SearchRequest, Depends()],
    service: SchoolService = Depends(get_school_service),
) -> SearchResponse:
    return service.search_schools(filters)


@router.get(
    "/{school_id}",
    response_model=SchoolProfileResponse,
    summary="School profile",
    description="Returns a full structured school profile with explicit missing-data metadata.",
)
def get_school_profile(
    school_id: int,
    service: SchoolService = Depends(get_school_service),
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
    return profile

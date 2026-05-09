from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from schemas.schools import SearchRequest, SearchResponse
from services.schools import SchoolService

router = APIRouter(prefix="/schools", tags=["schools"])


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

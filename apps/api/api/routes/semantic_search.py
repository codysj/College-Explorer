from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from repositories.schools import SchoolRepository
from schemas.semantic_search import SemanticSearchRequest, SemanticSearchResponse
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
) -> SemanticSearchResponse:
    return service.search(request)

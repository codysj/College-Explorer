from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from repositories.schools import SchoolRepository
from schemas.rankings import RankingRequest, RankingResponse
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
) -> RankingResponse:
    return service.rank_schools(request)

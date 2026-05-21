from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from repositories.schools import SchoolRepository
from schemas.sensitivity import SensitivityRequest, SensitivityResponse
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
) -> SensitivityResponse:
    return service.analyze(request)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from repositories.decision import DecisionRepository
from repositories.schools import SchoolRepository
from schemas.decision import (
    DecisionOffer,
    DecisionOfferCreate,
    DecisionOffersResponse,
    DecisionReportRequest,
    DecisionReportResponse,
)
from services.cache import CacheService
from services.decision import DecisionService
from services.ranking_service import RankingService

router = APIRouter(prefix="/decision", tags=["decision"])


def get_decision_service(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> DecisionService:
    return DecisionService(
        DecisionRepository(db),
        RankingService(SchoolRepository(db), cache),
    )


@router.post(
    "/offers",
    response_model=DecisionOffer,
    summary="Create or update an accepted/finalist offer",
)
def upsert_decision_offer(
    request: DecisionOfferCreate,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionOffer:
    return service.upsert_offer(request)


@router.get(
    "/offers",
    response_model=DecisionOffersResponse,
    summary="List accepted/finalist offers",
)
def list_decision_offers(
    user_id: int = Query(default=1, ge=1),
    service: DecisionService = Depends(get_decision_service),
) -> DecisionOffersResponse:
    return service.list_offers(user_id)


@router.post(
    "/report",
    response_model=DecisionReportResponse,
    summary="Generate a deterministic accepted-school decision report",
)
def build_decision_report(
    request: DecisionReportRequest,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionReportResponse:
    return service.build_report(request)

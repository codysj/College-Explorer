from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_cache_service, get_db
from api.routes.analytics import get_analytics_service
from repositories.decision import DecisionRepository
from repositories.schools import SchoolRepository
from schemas.analytics import AnalyticsEventCreate
from schemas.decision import (
    DecisionOffer,
    DecisionOfferCreate,
    DecisionOffersResponse,
    DecisionReportRequest,
    DecisionReportResponse,
)
from services.cache import CacheService
from services.analytics import AnalyticsService
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
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> DecisionReportResponse:
    try:
        response = service.build_report(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    analytics.try_log_event(
        AnalyticsEventCreate(
            user_id=request.user_id,
            event_name="decision_report_generated",
            entity_type="decision_report",
            entity_id=response.snapshot_id,
            metadata={
                "ranking_version": response.ranking_version,
                "report_version": response.report_version,
                "school_count": len(response.schools),
                "decision_confidence": response.decision_confidence,
            },
        )
    )
    return response

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from repositories.schools import SchoolRepository
from schemas.cost_calculator import CostCalculatorRequest, CostCalculatorResponse
from services.cost_calculator import CostCalculatorService

router = APIRouter(tags=["cost-calculator"])


def get_cost_calculator_service(db: Session = Depends(get_db)) -> CostCalculatorService:
    return CostCalculatorService(SchoolRepository(db))


@router.post(
    "/cost-calculator",
    response_model=CostCalculatorResponse,
    summary="Compare estimated college cost and directional value",
)
def calculate_cost_value(
    request: CostCalculatorRequest,
    service: CostCalculatorService = Depends(get_cost_calculator_service),
) -> CostCalculatorResponse:
    return service.calculate(request)

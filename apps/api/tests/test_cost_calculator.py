from fastapi.testclient import TestClient

from api.routes.cost_calculator import get_cost_calculator_service
from apps.api.main import app
from schemas.cost_calculator import CostCalculatorRequest
from services.cost_calculator import CostCalculatorService, monthly_payment


def make_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "school_id": 1,
        "name": "Berkeley Demo University",
        "city": "Berkeley",
        "state": "CA",
        "tuition_in_state": 15000,
        "tuition_out_state": 47000,
        "net_price": 28000,
        "average_aid": 14000,
        "debt_median": 16000,
        "graduation_rate": 0.9,
        "median_earnings": 79000,
        "repayment_rate": 0.88,
    }
    row.update(overrides)
    return row


class FakeCostRepository:
    def __init__(self) -> None:
        self.rows = [
            make_row(),
            make_row(
                school_id=2,
                name="USC Demo College",
                city="Los Angeles",
                net_price=48500,
                debt_median=26000,
                graduation_rate=0.86,
                median_earnings=72000,
                repayment_rate=0.82,
            ),
        ]

    def get_cost_calculator_rows(self, school_ids: list[int]) -> list[dict[str, object]]:
        return [row for row in self.rows if row["school_id"] in school_ids]


def make_service() -> CostCalculatorService:
    return CostCalculatorService(FakeCostRepository())


def test_calculates_four_year_cost_differences_and_value_summary() -> None:
    service = make_service()
    response = service.calculate(
        CostCalculatorRequest(
            schools=[
                {"school_id": 1, "estimated_yearly_cost": 22000, "annual_loan_amount": 5500},
                {"school_id": 2, "estimated_yearly_cost": 42500, "annual_loan_amount": 12000},
            ],
            baseline_school_id=1,
            max_annual_family_budget=30000,
        )
    )

    usc = next(item for item in response.results if item.school_id == 2)

    assert usc.estimated_four_year_total_cost == 170000
    assert usc.four_year_cost_difference == 82000
    assert usc.estimated_debt_exposure == 48000
    assert usc.affordability.status == "above_budget"
    assert any("$82,000 more" in item for item in response.comparison_summary)


def test_scholarships_and_aid_reduce_derived_yearly_cost() -> None:
    response = make_service().calculate(
        CostCalculatorRequest(
            schools=[{"school_id": 1, "estimated_net_price": 30000, "scholarships": 8000, "grants_aid": 5000}],
        )
    )

    result = response.results[0]

    assert result.estimated_yearly_cost == 17000
    assert result.estimated_four_year_total_cost == 68000
    assert "derived_yearly_cost" in result.warnings


def test_debt_sensitivity_scenarios_use_standard_amortization() -> None:
    response = make_service().calculate(
        CostCalculatorRequest(schools=[{"school_id": 1, "estimated_yearly_cost": 20000, "annual_loan_amount": 5000}])
    )

    scenarios = {item.scenario: item for item in response.results[0].repayment_scenarios}

    assert scenarios["base"].principal == 20000
    assert scenarios["base"].estimated_monthly_payment == monthly_payment(20000, 0.055, 10)
    assert scenarios["higher_debt"].principal == 30000


def test_missing_data_reduces_confidence_without_zero_defaults() -> None:
    repository = FakeCostRepository()
    repository.rows = [make_row(net_price=None, debt_median=None, graduation_rate=None, median_earnings=None)]
    response = CostCalculatorService(repository).calculate(CostCalculatorRequest(schools=[{"school_id": 1}]))

    result = response.results[0]

    assert result.estimated_yearly_cost is not None
    assert result.directional_outcome_adjusted_value == "uncertain"
    assert result.confidence in {"low", "medium"}
    assert "missing_outcomes_data" in result.warnings
    assert "missing_debt_assumption" in result.warnings


def test_invalid_numeric_inputs_return_validation_error(client: TestClient) -> None:
    response = client.post(
        "/cost-calculator",
        json={"schools": [{"school_id": 1, "estimated_yearly_cost": -1}]},
    )

    assert response.status_code == 422


def test_cost_calculator_endpoint_response_schema(client: TestClient) -> None:
    app.dependency_overrides[get_cost_calculator_service] = make_service
    try:
        response = client.post(
            "/cost-calculator",
            json={
                "schools": [
                    {"school_id": 1, "estimated_yearly_cost": 22000, "annual_loan_amount": 5500},
                    {"school_id": 2, "estimated_yearly_cost": 42500, "annual_loan_amount": 12000},
                ],
                "baseline_school_id": 1,
            },
        )
    finally:
        app.dependency_overrides.clear()

    payload = response.json()

    assert response.status_code == 200
    assert payload["calculator_version"] == "v1.0"
    assert payload["results"][0]["formulas"]
    assert payload["disclaimer"]

from fastapi.testclient import TestClient

from api.routes.rankings import get_ranking_service
from apps.api.main import app
from schemas.preferences import Preference
from services.ranking_service import RANKING_VERSION, RankingService, normalize_weights


def make_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "school_id": 1,
        "name": "Bayview Technical University",
        "city": "New Haven",
        "state": "CT",
        "region": "Northeast",
        "type": "Public",
        "setting": "Urban",
        "enrollment": 11800,
        "acceptance_rate": 0.52,
        "top_majors": ["Computer Science", "Engineering", "Data Science"],
        "graduation_rate": 0.78,
        "retention_rate": 0.87,
        "student_faculty_ratio": 14.0,
        "tuition_in_state": 15900,
        "tuition_out_state": 34900,
        "net_price": 24400,
        "average_aid": 14200,
        "debt_median": 23000,
        "median_earnings": 68000,
        "repayment_rate": 0.81,
        "housing_available": True,
        "sports_division": "DII",
        "greek_life_rate": 0.12,
        "culture_tags": ["technical", "urban", "career-focused"],
    }
    row.update(overrides)
    return row


class FakeRepository:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def get_ranking_candidate_rows(self, filters: object) -> list[dict[str, object]]:
        return self.rows


def make_service(rows: list[dict[str, object]] | None = None) -> RankingService:
    return RankingService(FakeRepository(rows or [make_row()]))


def test_academic_scoring_rewards_major_match() -> None:
    service = make_service()
    preference = Preference(intended_major="Computer Science")

    matched = service.score_academic_fit(make_row(), preference)
    unmatched = service.score_academic_fit(make_row(top_majors=["Biology"]), preference)

    assert matched.score > unmatched.score
    assert matched.reason_code == "academic_major_match"
    assert 0 <= matched.score <= 100


def test_cost_scoring_uses_budget_without_treating_missing_as_zero() -> None:
    service = make_service()
    preference = Preference(max_annual_cost=30000)

    within_budget = service.score_cost_fit(make_row(net_price=24000), preference)
    above_budget = service.score_cost_fit(make_row(net_price=45000), preference)
    missing = service.score_cost_fit(
        make_row(net_price=None, average_aid=None, tuition_out_state=None, tuition_in_state=None, debt_median=None),
        preference,
    )

    assert within_budget.score > above_budget.score
    assert within_budget.reason_code == "cost_within_budget"
    assert missing.score == 50.0
    assert missing.confidence == 0.0


def test_career_scoring_rewards_outcomes_and_priority_tags() -> None:
    service = make_service()
    preference = Preference(constraints={"career_priorities": ["High earnings", "Internships"]})

    strong = service.score_career_fit(make_row(), preference)
    weaker = service.score_career_fit(
        make_row(median_earnings=43000, repayment_rate=0.62, culture_tags=["outdoors"]),
        preference,
    )

    assert strong.score > weaker.score
    assert strong.reason_code in {"career_strong_earnings", "career_priority_match"}


def test_location_scoring_rewards_preferred_state_and_region() -> None:
    service = make_service()
    preference = Preference(home_state="CA", constraints={"preferred_states": ["CT"], "preferred_regions": ["Northeast"]})

    preferred = service.score_location_fit(make_row(state="CT", region="Northeast"), preference)
    other = service.score_location_fit(make_row(state="CA", region="West"), preference)

    assert preferred.score > other.score
    assert preferred.reason_code == "location_preferred_state"


def test_campus_scoring_rewards_lifestyle_matches() -> None:
    service = make_service()
    preference = Preference(
        constraints={
            "preferred_settings": ["Urban"],
            "preferred_school_types": ["Public"],
            "campus_preferences": ["Athletics", "Greek life"],
        }
    )

    matched = service.score_campus_lifestyle_fit(make_row(), preference)
    weaker = service.score_campus_lifestyle_fit(
        make_row(setting="Rural", type="Private", sports_division="DIII", greek_life_rate=0.02),
        preference,
    )

    assert matched.score > weaker.score
    assert matched.reason_code == "campus_preferred_setting"


def test_admissions_scoring_respects_strategy_and_acceptance_comfort() -> None:
    service = make_service()
    preference = Preference(constraints={"admissions_strategy": "likely", "target_acceptance_rate_min": 50})

    likely = service.score_admissions_realism(make_row(acceptance_rate=0.72), preference)
    reach = service.score_admissions_realism(make_row(acceptance_rate=0.20), preference)

    assert likely.score > reach.score
    assert reach.tradeoff_code == "admissions_below_acceptance_comfort"


def test_weighted_aggregation_normalizes_custom_weights() -> None:
    service = make_service()
    preference = Preference(
        intended_major="Computer Science",
        max_annual_cost=30000,
        weights={"cost": 10},
    )

    ranked = service.score_school(make_row(), preference)

    assert normalize_weights(preference.weights)["cost"] == 1.0
    assert ranked.fit_score == ranked.category_scores["cost"]


def test_hard_constraints_filter_cost_and_major_when_strict() -> None:
    rows = [
        make_row(school_id=1, top_majors=["Computer Science"], net_price=26000),
        make_row(school_id=2, top_majors=["Biology"], net_price=26000),
        make_row(school_id=3, top_majors=["Computer Science"], net_price=42000),
    ]
    service = make_service(rows)
    preference = Preference(
        intended_major="Computer Science",
        max_annual_cost=30000,
        constraints={"strict_major": True, "strict_cost": True},
    )

    ranked = service.rank_rows(rows, preference)

    assert [school.row["school_id"] for school in ranked] == [1]


def test_stable_ordering_is_deterministic_with_school_id_tie_breaker() -> None:
    rows = [
        make_row(school_id=2, name="Second College"),
        make_row(school_id=1, name="First College"),
    ]
    service = make_service(rows)
    preference = Preference()

    first_run = service.rank_rows(rows, preference)
    second_run = service.rank_rows(rows, preference)

    assert [school.row["school_id"] for school in first_run] == [1, 2]
    assert [school.row["school_id"] for school in second_run] == [1, 2]


def test_rankings_endpoint_returns_ranked_search_output(client: TestClient) -> None:
    rows = [
        make_row(school_id=1, name="Bayview Technical University"),
        make_row(
            school_id=2,
            name="Cedar Hill Liberal Arts College",
            top_majors=["English"],
            net_price=42000,
            median_earnings=48000,
            acceptance_rate=0.25,
        ),
    ]

    def override_ranking_service() -> RankingService:
        return make_service(rows)

    app.dependency_overrides[get_ranking_service] = override_ranking_service
    try:
        response = client.post(
            "/rankings",
            json={
                "preferences": {
                    "intended_major": "Computer Science",
                    "max_annual_cost": 30000,
                    "weights": {"academic": 0.4, "cost": 0.3, "career": 0.3},
                    "constraints": {"strict_cost": True},
                },
                "filters": {"page": 1, "page_size": 10},
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["ranking_version"] == RANKING_VERSION
    assert payload["total_results"] == 1
    assert payload["results"][0]["school_id"] == 1
    assert payload["results"][0]["fit_score"] is not None
    assert payload["results"][0]["confidence_score"] is not None
    assert payload["results"][0]["category_scores"]["academic"] >= 0
    assert payload["results"][0]["top_reasons"]
    assert payload["results"][0]["ranking_version"] == RANKING_VERSION

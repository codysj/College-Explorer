"""Pins ranked order against the real 92-school corpus.

Deferred from V3.2 because it needs real data. Every other ranking test uses a couple
of hand-built rows, which proves the scoring rules but says nothing about what a student
actually sees. This one runs the real seed file through the ranking engine and asserts
the resulting order, so a data refresh or a scoring tweak cannot silently reshuffle
results without someone reviewing the change.

When this fails, that is the test working. Read the diff: if the new order is correct,
update the snapshot in the same commit that changed the data or the scoring, and bump
RANKING_VERSION if the scoring itself moved.

Reads the CSV rather than the database so it runs in CI with no Postgres.
"""

import csv
from pathlib import Path

import pytest

from ingestion.college_data import bool_value, float_value, int_value, list_value, text_value
from schemas.preferences import Preference
from services.ranking_service import RANKING_VERSION, RankingService

SEED_PATH = Path(__file__).resolve().parents[3] / "data" / "seed" / "schools_seed.csv"

# The scoring rules this snapshot was captured under. A bump means the order below was
# reviewed against new scoring, not carried forward unexamined.
# v1.1 reviewed: only a tradeoff code changed (campus_preference_not_matched ->
# campus_data_unavailable). Scores and order are byte-identical to v1.0.
SNAPSHOT_RANKING_VERSION = "v1.1"


class SeedRepository:
    """Serves the committed seed file in the shape get_ranking_candidate_rows() returns."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def get_ranking_candidate_rows(self, filters: object) -> list[dict[str, object]]:
        return self.rows


def load_seed_rows() -> list[dict[str, object]]:
    with SEED_PATH.open(newline="", encoding="utf-8-sig") as file:
        raw_rows = list(csv.DictReader(file))

    rows: list[dict[str, object]] = []
    for raw in raw_rows:
        rows.append(
            {
                # unitid, not the database serial id: it is stable across reseeds, which
                # matters because it is the engine's final tiebreaker.
                "school_id": int_value(raw["unitid"]),
                "name": text_value(raw["name"]),
                "city": text_value(raw["city"]),
                "state": text_value(raw["state"]),
                "region": text_value(raw["region"]),
                "type": text_value(raw["type"]),
                "setting": text_value(raw["setting"]),
                "enrollment": int_value(raw["undergraduate_enrollment"]),
                "acceptance_rate": float_value(raw["acceptance_rate"]),
                "top_majors": list_value(raw["top_majors"]),
                "graduation_rate": float_value(raw["graduation_rate"]),
                "retention_rate": float_value(raw["retention_rate"]),
                "student_faculty_ratio": float_value(raw["student_faculty_ratio"]),
                "tuition_in_state": int_value(raw["tuition_in_state"]),
                "tuition_out_state": int_value(raw["tuition_out_state"]),
                "net_price": int_value(raw["net_price"]),
                "average_aid": int_value(raw["average_aid"]),
                "debt_median": int_value(raw["debt_median"]),
                "median_earnings": int_value(raw["median_earnings"]),
                "repayment_rate": float_value(raw["repayment_rate"]),
                "housing_available": bool_value(raw["housing_available"]),
                "sports_division": text_value(raw["sports_division"]),
                "greek_life_rate": float_value(raw["greek_life_rate"]),
                "culture_tags": list_value(raw["culture_tags"]),
            }
        )
    return rows


@pytest.fixture(scope="module")
def seed_rows() -> list[dict[str, object]]:
    assert SEED_PATH.exists(), f"seed corpus missing at {SEED_PATH}"
    return load_seed_rows()


def top_names(rows: list[dict[str, object]], preference: Preference, count: int = 10) -> list[str]:
    ranked = RankingService(SeedRepository(rows)).rank_rows(rows, preference)
    return [str(item.row["name"]) for item in ranked[:count]]


BUDGET_ENGINEER = Preference(
    intended_major="Engineering",
    home_state="CA",
    max_annual_cost=30000,
    weights={"academic": 0.30, "cost": 0.30, "career": 0.20, "campus": 0.10, "location": 0.10},
    constraints={"preferred_state": "CA", "admissions_strategy": "balanced"},
)

EARNINGS_FOCUSED = Preference(
    intended_major="Business",
    max_annual_cost=None,
    weights={"academic": 0.15, "cost": 0.10, "career": 0.50, "campus": 0.10, "admissions_realism": 0.15},
    constraints={"admissions_strategy": "likely"},
)


def test_snapshot_ranking_version_is_current() -> None:
    """Forces a snapshot review whenever the scoring version moves."""
    assert RANKING_VERSION == SNAPSHOT_RANKING_VERSION, (
        f"RANKING_VERSION is {RANKING_VERSION} but this snapshot was captured under "
        f"{SNAPSHOT_RANKING_VERSION}. Re-review the expected orders below, then update "
        "SNAPSHOT_RANKING_VERSION."
    )


def test_corpus_size_is_stable(seed_rows: list[dict[str, object]]) -> None:
    assert len(seed_rows) == 92, "seed corpus changed size; re-review the snapshots below"


def test_budget_conscious_engineer_ranking(seed_rows: list[dict[str, object]]) -> None:
    assert top_names(seed_rows, BUDGET_ENGINEER) == [
        # Six California schools lead, which is the location preference doing its job,
        # followed by strong out-of-state options rather than excluding them.
        "California Institute of Technology",
        "Stanford University",
        "University of California-Berkeley",
        "University of California-Los Angeles",
        "University of California-San Diego",
        "University of California-Davis",
        "Massachusetts Institute of Technology",
        "University of Notre Dame",
        "Princeton University",
        "Dartmouth College",
    ]


def test_earnings_focused_ranking(seed_rows: list[dict[str, object]]) -> None:
    # A "likely" admissions strategy plus heavy career weighting surfaces large publics
    # with strong business earnings, not the most selective schools in the corpus.
    assert top_names(seed_rows, EARNINGS_FOCUSED) == [
        "Brigham Young University",
        "Virginia Polytechnic Institute and State University",
        "University of Maryland-College Park",
        "University of Minnesota-Twin Cities",
        "Texas A&M University-College Station",
        "University of Illinois Urbana-Champaign",
        "University of Colorado Boulder",
        "Rutgers University-New Brunswick",
        "University of Wisconsin-Madison",
        "Purdue University-Main Campus",
    ]


def test_ranking_is_deterministic(seed_rows: list[dict[str, object]]) -> None:
    """Same inputs, same order - no dict or set iteration leaking into the result."""
    assert top_names(seed_rows, BUDGET_ENGINEER, 92) == top_names(seed_rows, BUDGET_ENGINEER, 92)


def test_schools_missing_inputs_still_rank_but_score_lower_confidence(
    seed_rows: list[dict[str, object]],
) -> None:
    """Missing data must lower confidence, never silently drop a school."""
    ranked = RankingService(SeedRepository(seed_rows)).rank_rows(seed_rows, EARNINGS_FOCUSED)
    incomplete = [item for item in ranked if item.row["median_earnings"] is None]

    complete = [item for item in ranked if item.row["median_earnings"] is not None]
    assert incomplete, "expected at least one school with unavailable earnings"
    assert complete

    # The real property: a gap has to cost confidence relative to peers, not merely
    # land below an arbitrary ceiling.
    worst_complete = min(item.confidence_score for item in complete)
    for item in incomplete:
        assert item.confidence_score <= worst_complete, (
            f"{item.row['name']} is missing earnings but is no less confident than "
            "every school that reports them"
        )


def test_over_budget_schools_rank_lower_but_are_not_removed(
    seed_rows: list[dict[str, object]],
) -> None:
    """The documented product decision: budget is a soft signal, not a hard filter."""
    ranked = RankingService(SeedRepository(seed_rows)).rank_rows(seed_rows, BUDGET_ENGINEER)
    over_budget = [
        item
        for item in ranked
        if item.row["net_price"] is not None and int(item.row["net_price"]) > 30000
    ]

    assert over_budget, "corpus should contain schools above a $30k budget"

    # They are present (not filtered out) but none of them leads the list.
    leader = ranked[0]
    assert leader not in over_budget, "an over-budget school should not top a budget-led profile"
    assert len(ranked) == len(seed_rows), "budget must not remove candidates"


def test_thin_categories_report_missing_data_not_a_failed_preference(
    seed_rows: list[dict[str, object]],
) -> None:
    """Absence of data must not be reported as a shortcoming of the school.

    Scorecard publishes no housing, athletics, or Greek-life figures, so with no campus
    preference stated the category has nothing to assess. It used to emit
    "campus_preference_not_matched", telling students a preference they never expressed
    had gone unmet.
    """
    ranked = RankingService(SeedRepository(seed_rows)).rank_rows(seed_rows, BUDGET_ENGINEER)
    tradeoffs = [code for item in ranked for code in item.top_tradeoffs]

    assert "campus_data_limited" in tradeoffs
    assert "campus_preference_not_matched" not in tradeoffs, (
        "no campus preference was stated, so a mismatch cannot be claimed"
    )


def test_a_matched_location_is_never_reported_as_a_mismatch(
    seed_rows: list[dict[str, object]],
) -> None:
    """The sharper case: a school that matches must not be told it does not.

    With only a home state (no explicit preferred_states) the location category carries
    0.35 confidence, which trips the low-confidence tradeoff branch. Before the fix a
    California school scored 90 on location, earned the "location_home_state" reason, and
    was simultaneously told "location_preference_not_matched".
    """
    home_state_only = Preference(
        intended_major="Engineering",
        home_state="CA",
        weights={"academic": 0.3, "cost": 0.3, "career": 0.2, "campus": 0.1, "location": 0.1},
    )
    ranked = RankingService(SeedRepository(seed_rows)).rank_rows(seed_rows, home_state_only)
    californians = [item for item in ranked if item.row["state"] == "CA"]

    assert californians
    for item in californians:
        assert "location_preference_not_matched" not in item.top_tradeoffs, (
            f"{item.row['name']} is in the student's home state"
        )

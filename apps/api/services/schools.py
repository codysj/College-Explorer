from sqlalchemy.orm import Session

from repositories.schools import SchoolRepository
from schemas.schools import (
    SchoolProfileAcademics,
    SchoolProfileCampusLife,
    SchoolProfileCost,
    SchoolProfileOutcomes,
    SchoolProfileResponse,
    SearchRequest,
    SearchResponse,
)


PROFILE_COMPLETENESS_FIELDS = (
    "school_id",
    "name",
    "city",
    "state",
    "region",
    "type",
    "setting",
    "enrollment",
    "academics.majors",
    "academics.popular_majors",
    "academics.graduation_rate",
    "academics.retention_rate",
    "academics.student_faculty_ratio",
    "cost.tuition_in_state",
    "cost.tuition_out_state",
    "cost.net_price",
    "cost.average_aid",
    "cost.debt_median",
    "outcomes.median_earnings",
    "outcomes.completion_rate",
    "outcomes.repayment_rate",
    "outcomes.outcome_percentiles",
    "campus_life.sports",
    "campus_life.greek_life",
    "campus_life.housing",
    "campus_life.weather_band",
    "campus_life.diversity_metrics",
    "campus_life.culture_tags",
)


class SchoolService:
    def __init__(self, db: Session) -> None:
        self.repository = SchoolRepository(db)

    def get_school_profile(self, school_id: int) -> SchoolProfileResponse | None:
        row = self.repository.get_school_profile_row(school_id)
        if row is None:
            return None

        top_majors = row["top_majors"]
        culture_tags = row["culture_tags"]
        profile = SchoolProfileResponse(
            school_id=int(row["school_id"]),
            name=str(row["name"]),
            city=str(row["city"]),
            state=str(row["state"]),
            region=str(row["region"]),
            type=str(row["type"]),
            setting=str(row["setting"]),
            enrollment=row["enrollment"],
            academics=SchoolProfileAcademics(
                majors=top_majors,
                popular_majors=top_majors,
                graduation_rate=self._to_float(row["graduation_rate"]),
                retention_rate=self._to_float(row["retention_rate"]),
                student_faculty_ratio=self._to_float(row["student_faculty_ratio"]),
            ),
            cost=SchoolProfileCost(
                tuition_in_state=row["tuition_in_state"],
                tuition_out_state=row["tuition_out_state"],
                net_price=row["net_price"],
                average_aid=row["average_aid"],
                debt_median=row["debt_median"],
            ),
            outcomes=SchoolProfileOutcomes(
                median_earnings=row["median_earnings"],
                completion_rate=None,
                repayment_rate=self._to_float(row["repayment_rate"]),
                outcome_percentiles=None,
            ),
            campus_life=SchoolProfileCampusLife(
                sports=row["sports_division"],
                greek_life=self._to_float(row["greek_life_rate"]),
                housing=row["housing_available"],
                weather_band=None,
                diversity_metrics=None,
                culture_tags=culture_tags,
            ),
            data_confidence_score=0,
        )
        missing_fields = self._missing_fields(profile)
        profile.data_fields_missing = missing_fields
        profile.data_confidence_score = round(
            (len(PROFILE_COMPLETENESS_FIELDS) - len(missing_fields)) / len(PROFILE_COMPLETENESS_FIELDS),
            4,
        )
        return profile

    def search_schools(self, filters: SearchRequest) -> SearchResponse:
        results, total_results = self.repository.search_schools(filters)
        return SearchResponse(
            results=results,
            page=filters.page,
            page_size=filters.page_size,
            total_results=total_results,
            has_next=filters.page * filters.page_size < total_results,
        )

    def _missing_fields(self, profile: SchoolProfileResponse) -> list[str]:
        payload = profile.model_dump()
        missing: list[str] = []
        for field in PROFILE_COMPLETENESS_FIELDS:
            value: object = payload
            for part in field.split("."):
                value = value[part] if isinstance(value, dict) else None
            if value is None:
                missing.append(field)
        return missing

    def _to_float(self, value: object) -> float | None:
        return float(value) if value is not None else None

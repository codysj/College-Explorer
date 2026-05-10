from time import perf_counter

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from core.logging import get_logger
from models.school import School, SchoolAcademics, SchoolCampusLife, SchoolCosts, SchoolOutcomes
from repositories.base import BaseRepository
from schemas.schools import SchoolSearchResult, SearchRequest

logger = get_logger(__name__)


class SchoolRepository(BaseRepository[School]):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_school_profile_row(self, school_id: int) -> dict[str, object] | None:
        query = (
            select(
                School.id.label("school_id"),
                School.name,
                School.city,
                School.state,
                School.region,
                School.type,
                School.setting,
                School.undergraduate_enrollment.label("enrollment"),
                SchoolAcademics.top_majors,
                SchoolAcademics.graduation_rate,
                SchoolAcademics.retention_rate,
                SchoolAcademics.student_faculty_ratio,
                SchoolCosts.tuition_in_state,
                SchoolCosts.tuition_out_state,
                SchoolCosts.net_price,
                SchoolCosts.average_aid,
                SchoolCosts.debt_median,
                SchoolOutcomes.median_earnings,
                SchoolOutcomes.repayment_rate,
                SchoolCampusLife.housing_available,
                SchoolCampusLife.sports_division,
                SchoolCampusLife.greek_life_rate,
                SchoolCampusLife.culture_tags,
            )
            .join(SchoolAcademics, SchoolAcademics.school_id == School.id, isouter=True)
            .join(SchoolCosts, SchoolCosts.school_id == School.id, isouter=True)
            .join(SchoolOutcomes, SchoolOutcomes.school_id == School.id, isouter=True)
            .join(SchoolCampusLife, SchoolCampusLife.school_id == School.id, isouter=True)
            .where(School.id == school_id)
        )
        row = self.db.execute(query).mappings().one_or_none()
        return dict(row) if row is not None else None

    def search_schools(self, filters: SearchRequest) -> tuple[list[SchoolSearchResult], int]:
        base_query = (
            select(
                School.id.label("school_id"),
                School.name,
                School.city,
                School.state,
                School.type,
                School.setting,
                School.undergraduate_enrollment.label("enrollment"),
                School.acceptance_rate,
                SchoolCosts.net_price,
                SchoolAcademics.graduation_rate,
            )
            .join(SchoolCosts, SchoolCosts.school_id == School.id, isouter=True)
            .join(SchoolAcademics, SchoolAcademics.school_id == School.id, isouter=True)
        )
        filtered_query = self._apply_filters(base_query, filters)

        total_results = self.db.scalar(
            select(func.count()).select_from(filtered_query.order_by(None).subquery())
        )
        total = int(total_results or 0)

        sorted_query = self._apply_sort(filtered_query, filters)
        paged_query = sorted_query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)

        start = perf_counter()
        rows = self.db.execute(paged_query).mappings().all()
        duration_ms = round((perf_counter() - start) * 1000, 2)

        results = [
            SchoolSearchResult(
                school_id=row["school_id"],
                name=row["name"],
                city=row["city"],
                state=row["state"],
                type=row["type"],
                setting=row["setting"],
                enrollment=row["enrollment"],
                acceptance_rate=float(row["acceptance_rate"]) if row["acceptance_rate"] is not None else None,
                net_price=row["net_price"],
                graduation_rate=float(row["graduation_rate"]) if row["graduation_rate"] is not None else None,
            )
            for row in rows
        ]
        logger.info(
            "school_search_query",
            extra={
                "duration_ms": duration_ms,
                "row_count": len(results),
                "total_results": total,
                "page": filters.page,
                "page_size": filters.page_size,
            },
        )
        return results, total

    def get_ranking_candidate_rows(self, filters: SearchRequest) -> list[dict[str, object]]:
        query = (
            select(
                School.id.label("school_id"),
                School.name,
                School.city,
                School.state,
                School.region,
                School.type,
                School.setting,
                School.undergraduate_enrollment.label("enrollment"),
                School.acceptance_rate,
                SchoolAcademics.top_majors,
                SchoolAcademics.graduation_rate,
                SchoolAcademics.retention_rate,
                SchoolAcademics.student_faculty_ratio,
                SchoolCosts.tuition_in_state,
                SchoolCosts.tuition_out_state,
                SchoolCosts.net_price,
                SchoolCosts.average_aid,
                SchoolCosts.debt_median,
                SchoolOutcomes.median_earnings,
                SchoolOutcomes.repayment_rate,
                SchoolCampusLife.housing_available,
                SchoolCampusLife.sports_division,
                SchoolCampusLife.greek_life_rate,
                SchoolCampusLife.culture_tags,
            )
            .join(SchoolAcademics, SchoolAcademics.school_id == School.id, isouter=True)
            .join(SchoolCosts, SchoolCosts.school_id == School.id, isouter=True)
            .join(SchoolOutcomes, SchoolOutcomes.school_id == School.id, isouter=True)
            .join(SchoolCampusLife, SchoolCampusLife.school_id == School.id, isouter=True)
        )
        filtered_query = self._apply_filters(query, filters).order_by(School.id.asc())
        rows = self.db.execute(filtered_query).mappings().all()
        return [dict(row) for row in rows]

    def _apply_filters(self, query: Select[tuple], filters: SearchRequest) -> Select[tuple]:
        if filters.query:
            query = query.where(School.name.ilike(f"%{filters.query}%"))
        if filters.state:
            query = query.where(School.state == filters.state.upper())
        if filters.region:
            query = query.where(School.region == filters.region)
        if filters.type:
            query = query.where(School.type == filters.type)
        if filters.setting:
            query = query.where(School.setting == filters.setting)
        if filters.min_enrollment is not None:
            query = query.where(School.undergraduate_enrollment >= filters.min_enrollment)
        if filters.max_enrollment is not None:
            query = query.where(School.undergraduate_enrollment <= filters.max_enrollment)
        if filters.min_net_price is not None:
            query = query.where(SchoolCosts.net_price >= filters.min_net_price)
        if filters.max_net_price is not None:
            query = query.where(SchoolCosts.net_price <= filters.max_net_price)
        if filters.min_acceptance_rate is not None:
            query = query.where(School.acceptance_rate >= filters.min_acceptance_rate)
        if filters.max_acceptance_rate is not None:
            query = query.where(School.acceptance_rate <= filters.max_acceptance_rate)
        if filters.min_graduation_rate is not None:
            query = query.where(SchoolAcademics.graduation_rate >= filters.min_graduation_rate)
        if filters.max_graduation_rate is not None:
            query = query.where(SchoolAcademics.graduation_rate <= filters.max_graduation_rate)
        return query

    def _apply_sort(self, query: Select[tuple], filters: SearchRequest) -> Select[tuple]:
        sort_columns = {
            "name": School.name,
            "net_price": SchoolCosts.net_price,
            "graduation_rate": SchoolAcademics.graduation_rate,
            "acceptance_rate": School.acceptance_rate,
            "enrollment": School.undergraduate_enrollment,
        }
        sort_column = sort_columns[filters.sort]
        sort_expression = sort_column.desc().nulls_last() if filters.direction == "desc" else sort_column.asc().nulls_last()
        return query.order_by(sort_expression, School.id.asc())

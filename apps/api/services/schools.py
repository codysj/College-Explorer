from sqlalchemy.orm import Session

from models.school import School
from repositories.schools import SchoolRepository
from schemas.schools import SearchRequest, SearchResponse


class SchoolService:
    def __init__(self, db: Session) -> None:
        self.repository = SchoolRepository(db)

    def get_school_by_id(self, school_id: int) -> School | None:
        return self.repository.get_school_by_id(school_id)

    def search_schools(self, filters: SearchRequest) -> SearchResponse:
        results, total_results = self.repository.search_schools(filters)
        return SearchResponse(
            results=results,
            page=filters.page,
            page_size=filters.page_size,
            total_results=total_results,
            has_next=filters.page * filters.page_size < total_results,
        )

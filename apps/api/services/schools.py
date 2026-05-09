from sqlalchemy.orm import Session

from models.school import School
from repositories.schools import SchoolRepository


class SchoolService:
    def __init__(self, db: Session) -> None:
        self.repository = SchoolRepository(db)

    def get_school_by_id(self, school_id: int) -> School | None:
        return self.repository.get_school_by_id(school_id)

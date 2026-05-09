from sqlalchemy.orm import Session

from models.school import School
from repositories.base import BaseRepository


class SchoolRepository(BaseRepository[School]):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_school_by_id(self, school_id: int) -> School | None:
        """Example repository method for future routes and services."""
        return self.db.get(School, school_id)

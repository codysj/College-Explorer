from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.decision import AcceptanceOffer, DecisionSummarySnapshot
from models.school import School, SchoolAcademics, SchoolCampusLife, SchoolCosts, SchoolOutcomes
from models.user import SavedSchool, User
from schemas.decision import DecisionOfferCreate


class DecisionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ensure_demo_user(self, user_id: int) -> None:
        if self.db.get(User, user_id) is not None:
            return
        self.db.add(User(id=user_id, email=None, display_name="Local decision workspace", auth_provider="local"))
        self.db.flush()

    def upsert_offer(self, request: DecisionOfferCreate) -> dict[str, object]:
        self.ensure_demo_user(request.user_id)
        offer = self.db.execute(
            select(AcceptanceOffer).where(
                AcceptanceOffer.user_id == request.user_id,
                AcceptanceOffer.school_id == request.school_id,
            )
        ).scalar_one_or_none()

        if offer is None:
            offer = AcceptanceOffer(user_id=request.user_id, school_id=request.school_id)
            self.db.add(offer)

        offer.status = request.status
        offer.aid_offer = request.aid_offer
        offer.scholarships = request.scholarships
        offer.estimated_yearly_cost = request.estimated_yearly_cost
        offer.visit_notes = request.visit_notes
        offer.unresolved_concerns = request.unresolved_concerns
        offer.parent_priority_notes = request.parent_priority_notes
        offer.student_priority_notes = request.student_priority_notes

        self._upsert_saved_school_status(request.user_id, request.school_id, request.status)
        self.db.flush()
        self.db.commit()
        return self.get_offer_row(request.user_id, request.school_id) or {}

    def get_offer_rows(self, user_id: int, school_ids: list[int] | None = None) -> list[dict[str, object]]:
        query = (
            select(
                AcceptanceOffer.id,
                AcceptanceOffer.user_id,
                AcceptanceOffer.school_id,
                AcceptanceOffer.status,
                AcceptanceOffer.aid_offer,
                AcceptanceOffer.scholarships,
                AcceptanceOffer.estimated_yearly_cost,
                AcceptanceOffer.visit_notes,
                AcceptanceOffer.unresolved_concerns,
                AcceptanceOffer.parent_priority_notes,
                AcceptanceOffer.student_priority_notes,
                AcceptanceOffer.created_at,
                AcceptanceOffer.updated_at,
                School.name.label("school_name"),
                School.city,
                School.state,
            )
            .join(School, School.id == AcceptanceOffer.school_id)
            .where(AcceptanceOffer.user_id == user_id)
            .order_by(AcceptanceOffer.status.desc(), School.name.asc(), AcceptanceOffer.school_id.asc())
        )
        if school_ids:
            query = query.where(AcceptanceOffer.school_id.in_(school_ids))
        return [dict(row) for row in self.db.execute(query).mappings().all()]

    def get_offer_row(self, user_id: int, school_id: int) -> dict[str, object] | None:
        rows = self.get_offer_rows(user_id, [school_id])
        return rows[0] if rows else None

    def get_decision_candidate_rows(self, school_ids: list[int]) -> list[dict[str, object]]:
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
            .where(School.id.in_(school_ids))
            .order_by(School.id.asc())
        )
        return [dict(row) for row in self.db.execute(query).mappings().all()]

    def save_snapshot(
        self,
        user_id: int,
        summary_version: str,
        school_ids: list[int],
        summary: dict[str, object],
    ) -> int:
        self.ensure_demo_user(user_id)
        snapshot = DecisionSummarySnapshot(
            user_id=user_id,
            summary_version=summary_version,
            school_ids=school_ids,
            summary=summary,
        )
        self.db.add(snapshot)
        self.db.flush()
        self.db.commit()
        return int(snapshot.id)

    def _upsert_saved_school_status(self, user_id: int, school_id: int, status: str) -> None:
        saved = self.db.execute(
            select(SavedSchool).where(SavedSchool.user_id == user_id, SavedSchool.school_id == school_id)
        ).scalar_one_or_none()
        if saved is None:
            self.db.add(SavedSchool(user_id=user_id, school_id=school_id, status=status))
        else:
            saved.status = status

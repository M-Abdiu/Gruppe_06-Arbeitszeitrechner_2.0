"""
Repository für Violation-Persistierung.
"""
from typing import List, Optional

from sqlmodel import Session, select

from src.domain.violations import Violation
from src.persistence.mappers import ViolationMapper
from src.persistence.models import Violation as DBViolation


class ViolationRepository:
    """Persistiert und lädt Violation-Objekte aus der Datenbank."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, violation: Violation, time_entry_id: Optional[int] = None) -> Violation:
        """Speichert eine Violation in die DB."""
        db_violation = ViolationMapper.to_db(violation, time_entry_id)
        self.session.add(db_violation)
        self.session.commit()
        self.session.refresh(db_violation)
        return ViolationMapper.to_domain(db_violation)

    def save_many(
        self,
        violations: List[Violation],
        time_entry_id: Optional[int] = None,
        commit: bool = True,
    ) -> List[Violation]:
        """Speichert mehrere Violations in einem Schritt."""
        if not violations:
            return []

        db_violations = [ViolationMapper.to_db(violation, time_entry_id) for violation in violations]
        self.session.add_all(db_violations)

        if commit:
            self.session.commit()
            for db_violation in db_violations:
                self.session.refresh(db_violation)

        return [ViolationMapper.to_domain(db_violation) for db_violation in db_violations]

    def find_by_time_entry_id(self, time_entry_id: int) -> List[Violation]:
        """Lädt alle Violations für einen bestimmten TimeEntry."""
        db_violations = self.session.exec(
            select(DBViolation).where(DBViolation.fk_TimeEntry_id == time_entry_id)
        ).all()
        return [ViolationMapper.to_domain(db_violation) for db_violation in db_violations]

    def delete_by_time_entry_id(self, time_entry_id: int, commit: bool = True) -> bool:
        """Löscht alle Violations zu einem TimeEntry."""
        db_violations = self.session.exec(
            select(DBViolation).where(DBViolation.fk_TimeEntry_id == time_entry_id)
        ).all()
        if not db_violations:
            return False

        for db_violation in db_violations:
            self.session.delete(db_violation)
        if commit:
            self.session.commit()
        return True
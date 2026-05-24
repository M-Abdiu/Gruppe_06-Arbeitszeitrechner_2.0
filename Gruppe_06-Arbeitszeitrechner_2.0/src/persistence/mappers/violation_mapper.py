"""
Mapper für Violation-Konvertierung zwischen Domain und Persistence Layer.
"""
from typing import Optional

from src.domain.violations import Violation
from src.persistence.models import Violation as DBViolation


class ViolationMapper:
    """Konvertiert zwischen Domain-Violation und DB-Violation."""

    @staticmethod
    def to_db(violation: Violation, time_entry_id: Optional[int] = None) -> DBViolation:
        """Domain Model → Database Model"""
        return DBViolation(
            pk_violation_id=None,
            fk_TimeEntry_id=time_entry_id,
            type=violation.type,
            message=violation.message,
            violation_date=violation.date,
        )

    @staticmethod
    def to_domain(db_violation: DBViolation) -> Violation:
        """Database Model → Domain Model"""
        return Violation(
            type=db_violation.type,
            message=db_violation.message,
            date=db_violation.violation_date,
        )
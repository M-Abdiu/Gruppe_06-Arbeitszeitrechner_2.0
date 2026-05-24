import uuid
from abc import ABC, abstractmethod
from typing import Optional

class User(ABC):
    """Abstrakte Basisklasse für alle Systembenutzer mit rollenbasierter Unterscheidung."""
    def __init__(self, first_name: str, last_name: str, email: str, user_role: str, entity_id: Optional[str] = None) -> None:
        self.id: str = entity_id or str(uuid.uuid4())
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.email: str = email
        self.role: str = user_role

    @abstractmethod
    def has_admin_privileges(self) -> bool:
        """Jede Rolle entscheidet selbst, ob Administratorrechte gegeben sind."""
        pass


class Employee(User):
    """Mitarbeitender mit Pensum und Sollzeiten-Berechnung."""

    def __init__(self, first_name: str, last_name: str, email: str, employment_percentage: float, entity_id: Optional[str] = None) -> None:
        super().__init__(first_name, last_name, email, user_role="Employee", entity_id=entity_id)
        if not (0.0 <= employment_percentage <= 100.0):
            raise ValueError("Pensum muss zwischen 0 und 100 liegen.")
        self.employment_percentage: float = employment_percentage

    def get_weekly_target_hours(self) -> float:
        """Berechnet die individuelle Sollzeit anhand des Pensums."""
        from .config import WorkRulesConfig
        return (WorkRulesConfig.BASE_WEEKLY_HOURS / 100.0) * self.employment_percentage

    def has_admin_privileges(self) -> bool:
        """Mitarbeiter haben keine Admin-Rechte."""
        return False


class Admin(User):
    """Admin-Rolle mit Verwaltungsrechten."""
    def __init__(self, first_name: str, last_name: str, email: str, entity_id: Optional[str] = None) -> None:
        super().__init__(first_name, last_name, email, user_role="Admin", entity_id=entity_id)

    def has_admin_privileges(self) -> bool:
        """Admin hat immer volle Rechte."""
        return True

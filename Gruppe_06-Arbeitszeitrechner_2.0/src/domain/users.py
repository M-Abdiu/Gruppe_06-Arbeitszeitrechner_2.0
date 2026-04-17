import uuid
from abc import ABC
from typing import Optional

class User(ABC):
    """Abstrakte Basisklasse für alle Systembenutzer."""
    def __init__(self, first_name: str, last_name: str, email: str, user_role: str, entity_id: Optional[str] = None):
        self.id: str = entity_id or str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = user_role


class Employee(User):
    """Mitarbeitender mit Pensum und Sollzeiten-Berechnung."""
    BASE_WEEKLY_HOURS = 42.0  # Konstante Basis-Arbeitszeit bei 100%

    def __init__(self, first_name: str, last_name: str, email: str, employment_percentage: float, entity_id: Optional[str] = None):
        super().__init__(first_name, last_name, email, user_role="Employee", entity_id=entity_id)
        if not (0.0 <= employment_percentage <= 100.0):
            raise ValueError("Pensum muss zwischen 0 und 100 liegen.")
        self.employment_percentage = employment_percentage

    def get_weekly_target_hours(self) -> float:
        """Berechnet die individuelle Sollzeit anhand des Pensums."""
        return (self.BASE_WEEKLY_HOURS / 100.0) * self.employment_percentage


class Admin(User):
    """Admin-Rolle für Prüfungsrechte."""
    def __init__(self, first_name: str, last_name: str, email: str, entity_id: Optional[str] = None):
        super().__init__(first_name, last_name, email, user_role="Admin", entity_id=entity_id)

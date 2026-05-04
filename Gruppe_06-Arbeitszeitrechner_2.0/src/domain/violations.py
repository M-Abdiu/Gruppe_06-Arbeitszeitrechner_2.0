from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Violation:
    """Repräsentiert einen fachlichen Regelverstoss."""
    type: str
    message: str
    date: Optional[date] = None

    def __str__(self) -> str:
        date_str: str = f" am {self.date}" if self.date else ""
        return f"Verstoss ({self.type}){date_str}: {self.message}"

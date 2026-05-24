"""
Zentrale Konfiguration für Geschäftslogik und Arbeitsregelwerte.
Diese Klasse vermeidet Magic Numbers und ermöglicht einfache Regeländerungen.
"""
from datetime import timedelta


class WorkRulesConfig:
    """Unveränderliche Konstanten für Arbeitszeit-Regeln."""
    
    # Basis-Arbeitszeitrahmen
    BASE_WEEKLY_HOURS = 42.0  # Vollzeitangestellte arbeiten 42h/Woche
    
    # Pausenregelung (Fix)
    MAX_HOURS_WITHOUT_BREAK = timedelta(hours=5, minutes=30)  # Nach 5.5h ohne Pause muss Pausen-Regelung greifen
    MIN_BREAK_HOURS = timedelta(minutes=15)  # Mindestens 15min Pause erforderlich, fixiert.
    
    # Tagesarbeitszeit-Grenze
    MAX_DAILY_HOURS = timedelta(hours=14)  # Niemand darf mehr als 14h/Tag arbeiten
    
    # Wochenarbeitszeit-Grenze
    MAX_WEEKLY_HOURS = timedelta(hours=50)  # Niemand darf mehr als 50h/Woche arbeiten
    
    @classmethod
    def validate_rules(cls) -> bool:
        """Überprüft, dass die Regeln konsistent sind."""
        assert cls.MAX_DAILY_HOURS > timedelta(0), "Maximale Tagesarbeitszeit muss > 0 sein"
        assert cls.MAX_WEEKLY_HOURS > cls.MAX_DAILY_HOURS, "Wochenmaximum muss > Tagesmaximum sein"
        assert cls.MIN_BREAK_HOURS > timedelta(0), "Mindest-Pausenzeit muss > 0 sein"
        return True

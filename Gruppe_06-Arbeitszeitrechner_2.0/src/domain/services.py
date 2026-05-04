from datetime import date, time, timedelta
from typing import List, Optional, Dict, Any
from .users import Employee
from .time_tracking import TimeEntry, Workweek, BreakTimeRule, MaxDailyWorkRule, MaxWeeklyWorkRule
from .violations import Violation


class TimeTrackingService:
    """
    Application Service zur Orchestrierung von Domain Logik und Persistenzschicht.
    
    Warum hier: Bildet eine Facade für die Geschäftslogik-Anwendungsfälle.
    Dependency Injection ermöglicht flexible Persistierungs-Strategien (DB, File, In-Memory, etc).
    """
    
    def __init__(self, repository: Optional[Any] = None) -> None:
        """
        Initialisiert den Service mit optionalem Repository.
        Falls None: In-Memory Speicherung (Testing, Demo).
        Falls implementiert: Echte DB-Persistierung.
        """
        self.repository = repository
        self.daily_rules = [BreakTimeRule(), MaxDailyWorkRule()]
        self.weekly_rules = [MaxWeeklyWorkRule()]
        # In-Memory Fallback für Testing ohne DB
        self._entries_cache: Dict[date, TimeEntry] = {}

    def add_work_day(self, employee: Employee, entry_date: date,
                     morning_start: time, morning_end: time,
                     afternoon_start: Optional[time] = None, 
                     afternoon_end: Optional[time] = None,
                     reference_date: Optional[date] = None) -> tuple[TimeEntry, List[Violation]]:
        """
        Erfasst einen Arbeitstag und prüft die täglichen Verstösse.
        
        :param employee: Der Mitarbeiter, der Zeit erfasst
        :param entry_date: Datum der Arbeit
        :param morning_start: Morgen-Startzeit
        :param morning_end: Morgen-Endzeit
        :param afternoon_start: Nachmittags-Startzeit (optional)
        :param afternoon_end: Nachmittags-Endzeit (optional)
        :param reference_date: Vergleichs-Datum für Zukunftsprüfung
        :return: Tuple aus (TimeEntry, [Violations])
        """
        entry: TimeEntry = TimeEntry(
            entry_date, morning_start, morning_end, 
            afternoon_start, afternoon_end, reference_date=reference_date or date.today()
        )
        
        violations: List[Violation] = []
        for rule in self.daily_rules:
            violations.extend(rule.check(entry))
        
        # Persistierung (falls Repository vorhanden)
        if self.repository:
            entry = self.repository.save(entry)
        else:
            # Fallback: In-Memory Cache
            if entry_date not in self._entries_cache:
                self._entries_cache[entry_date] = entry
            
        return entry, violations

    def evaluate_week(self, employee: Employee, year: int, calendar_week: int, entries: List[TimeEntry]) -> tuple[Workweek, List[Violation]]:
        """
        Baut eine Woche aus Einträgen zusammen und prüft wochenbasierte Verstösse.
        
        :param employee: Der Mitarbeiter
        :param year: Jahr
        :param calendar_week: Kalenderwoche (1-53)
        :param entries: Liste der TimeEntry-Objekte für diese Woche
        :return: Tuple aus (Workweek, [Violations])
        """
        week: Workweek = Workweek(employee, calendar_week, year)
        for entry in entries:
            week.add_entry(entry)
            
        violations: List[Violation] = []
        for rule in self.weekly_rules:
            violations.extend(rule.check(week))
        
        # Auch alle täglichen Verstösse sammeln
        for entry in entries:
            violations.extend(entry.get_daily_violations())
            
        return week, violations

    def get_employee_weekly_summary(self, employee: Employee, year: int, calendar_week: int) -> Dict[str, Any]:
        """
        Gibt eine Zusammenfassung der Wochenarbeit für einen Mitarbeiter.
        Hilfreich für Reports und UI-Darstellung.
        
        :param employee: Der Mitarbeiter
        :param year: Jahr
        :param calendar_week: Kalenderwoche
        :return: Dict mit Auswertungs-Daten und Violations
        """
        entries: List[TimeEntry] = self.repository.find_entries_for_week(employee.id, year, calendar_week) if self.repository else []
        week, violations = self.evaluate_week(employee, year, calendar_week, entries)
        
        total_hours: float = week.get_total_hours().total_seconds() / 3600.0
        target_hours: float = week.calculate_target_hours().total_seconds() / 3600.0
        overtime: float = week.calculate_overtime().total_seconds() / 3600.0
        
        return {
            "employee": employee,
            "calendar_week": calendar_week,
            "year": year,
            "total_hours": total_hours,
            "target_hours": target_hours,
            "overtime": overtime,
            "violations": violations,
            "entries": entries,
        }

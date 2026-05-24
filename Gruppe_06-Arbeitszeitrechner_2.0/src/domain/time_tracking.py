from datetime import date, time, timedelta, datetime
from typing import Optional, List
import uuid
from .users import Employee
from .violations import Violation
from .config import WorkRulesConfig

class TimeEntry:
    """Repräsentiert einen vollständig abgeschlossenen Arbeitstag."""
    
    def __init__(self, entry_date: date, 
                 morning_start: time, morning_end: time,
                 afternoon_start: Optional[time] = None, afternoon_end: Optional[time] = None,
                 reference_date: Optional[date] = None,
                 entry_id: Optional[str] = None):
        
        self.id: str = entry_id or str(uuid.uuid4())
        self.date: date = entry_date
        self.morning_start: time = morning_start
        self.morning_end: time = morning_end
        self.afternoon_start: Optional[time] = afternoon_start
        self.afternoon_end: Optional[time] = afternoon_end

        # Sofortige Validierung der Vollständigkeit & logischen Reihenfolge
        self._validate_times(reference_date)

    def _validate_times(self, reference_date: Optional[date]) -> None:
        """Stellt sicher, dass die Zeiten chronologisch korrekt und vollständig sind (reine Tagarbeit)."""
        if reference_date and self.date > reference_date:
            raise ValueError("Fachlicher Fehler: Es können keine Arbeitszeiten für die Zukunft erfasst werden.")

        def get_dt(t: time) -> datetime:
            return datetime.combine(date.min, t)

        if get_dt(self.morning_end) <= get_dt(self.morning_start):
            raise ValueError("Morgen-Endzeit muss nach der Morgen-Startzeit liegen (Nachtschicht ist nicht erlaubt).")

        # Wenn ein Nachmittag eingetragen ist, müssen Start UND Ende existieren
        if (self.afternoon_start and not self.afternoon_end) or (not self.afternoon_start and self.afternoon_end):
            raise ValueError("Nachmittagsblock muss vollständig sein (Start und Ende).")

        if self.afternoon_start and self.afternoon_end:
            if get_dt(self.afternoon_start) < get_dt(self.morning_end):
                 raise ValueError("Nachmittags-Startzeit darf nicht vor Morgen-Endzeit liegen.")
            if get_dt(self.afternoon_end) <= get_dt(self.afternoon_start):
                 raise ValueError("Nachmittags-Endzeit muss nach der Nachmittags-Startzeit liegen (Nachtschicht ist nicht erlaubt).")

    def calculate_work_hours(self) -> timedelta:
        """Berechnet die reine Netto-Arbeitszeit dieses Tages."""
        def get_dt(t: time) -> datetime:
            return datetime.combine(date.min, t)
        
        morning_work: timedelta = get_dt(self.morning_end) - get_dt(self.morning_start)
        afternoon_work: timedelta = timedelta()
        
        if self.afternoon_start and self.afternoon_end:
            afternoon_work = get_dt(self.afternoon_end) - get_dt(self.afternoon_start)
            
        return morning_work + afternoon_work

    def calculate_break_time(self) -> timedelta:
        """Berechnet die Mittagspause (sofern es einen Nachmittagsblock gibt)."""
        if self.afternoon_start and self.afternoon_end:
            return datetime.combine(date.min, self.afternoon_start) - datetime.combine(date.min, self.morning_end)
        return timedelta()

class Workweek:
    """Aggregiert Zeiteinträge einer Woche und berechnet Überstunden/Wochensolls."""
    
    def __init__(self, employee: Employee, calendar_week: int, year: int, week_id: Optional[str] = None):
        self.id: str = week_id or str(uuid.uuid4())
        self.employee: Employee = employee
        self.calendar_week: int = calendar_week
        self.year: int = year
        self.entries: List[TimeEntry] = []

    def add_entry(self, entry: TimeEntry) -> None:
        """Fügt einen neuen Tag zur Woche hinzu."""
        iso_year, iso_week, _ = entry.date.isocalendar()
        if iso_year != self.year or iso_week != self.calendar_week:
            raise ValueError(f"Eintragdatum {entry.date} (ISO: KW {iso_week}/{iso_year}) passt nicht zu KW {self.calendar_week}/{self.year}.")
            
        if any(e.date == entry.date for e in self.entries):
            raise ValueError(f"Ein Eintrag für das Datum {entry.date} existiert bereits in dieser Woche.")
            
        self.entries.append(entry)

    def get_total_hours(self) -> timedelta:
        """Summiert die gearbeitete Zeit aller Tage dieser Woche als timedelta."""
        return sum((e.calculate_work_hours() for e in self.entries), timedelta())

    def calculate_target_hours(self) -> timedelta:
        """Ermittelt das Wochensoll dieses spezifischen Mitarbeiters als timedelta."""
        target_hours_float: float = self.employee.get_weekly_target_hours()
        return timedelta(hours=target_hours_float)

    def calculate_overtime(self) -> timedelta:
        """Berechnet die Überstunden (Ist - Soll) als timedelta. Negativ bei Minusstunden."""
        return self.get_total_hours() - self.calculate_target_hours()

    def __repr__(self) -> str:
        return f"<Workweek KW {self.calendar_week}/{self.year} (Employee: {self.employee.first_name}, ID: {self.id}), Entries: {len(self.entries)}>"


# ==============================================================================
# STRATEGY PATTERN (Rules)
# ==============================================================================

class BreakTimeRule:
    """
    Strategie zur Prüfung der Pausenzeit. Es gilt fix eine 15-Minuten-Regel ohne Ausnahmen.
    Warum hier: Entkoppelt das Arbeitszeitgesetz von der Datenstruktur (TimeEntry).
    """

    def check(self, entry: TimeEntry) -> List[Violation]:
        violations: List[Violation] = []
        work_time: timedelta = entry.calculate_work_hours()
        break_time: timedelta = entry.calculate_break_time()

        if work_time > WorkRulesConfig.MAX_HOURS_WITHOUT_BREAK and break_time < WorkRulesConfig.MIN_BREAK_HOURS:
            violations.append(Violation(
                "Pausenregelung", 
                f"Es wurde keine ausreichende Pause (mindestens {WorkRulesConfig.MIN_BREAK_HOURS.total_seconds()/60:.0f} Min) gemacht.", 
                entry.date
            ))
        return violations

class MaxDailyWorkRule:
    """
    Strategie zur Prüfung der maximalen Tagesarbeitszeit.
    """

    def check(self, entry: TimeEntry) -> List[Violation]:
        violations: List[Violation] = []
        work_time: timedelta = entry.calculate_work_hours()
        
        if work_time > WorkRulesConfig.MAX_DAILY_HOURS:
            violations.append(Violation(
                "Maximalarbeitszeit", 
                f"Die Tagesarbeitszeit liegt über {WorkRulesConfig.MAX_DAILY_HOURS.total_seconds()/3600:.0f} Stunden ({work_time.total_seconds()/3600:.1f}h).", 
                entry.date
            ))
        return violations

class MaxWeeklyWorkRule:
    """
    Strategie zur Prüfung der maximalen Wochenarbeitszeit.
    """

    def check(self, week: Workweek) -> List[Violation]:
        violations: List[Violation] = []
        total_time: timedelta = week.get_total_hours()
        
        if total_time > WorkRulesConfig.MAX_WEEKLY_HOURS:
            violations.append(Violation(
                "Wochenhöchstarbeitszeit",
                f"Maximale Wochenarbeitszeit von {WorkRulesConfig.MAX_WEEKLY_HOURS.total_seconds()/3600:.0f}h überschritten ({total_time.total_seconds()/3600:.1f}h).",
                None
            ))
        return violations

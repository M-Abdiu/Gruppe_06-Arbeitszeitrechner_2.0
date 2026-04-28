from datetime import date, time, timedelta
from typing import List, Optional
from .users import Employee
from .time_tracking import TimeEntry, Workweek, BreakTimeRule, MaxDailyWorkRule, MaxWeeklyWorkRule
from .violations import Violation

class TimeTrackingService:
    """
    Application Service zur Orchestrierung von Domain Logik und Persistenzschicht.
    
    Warum hier: Bildet eine Facade für die Geschäftslogik-Anwendungsfälle.
    Alternative: Direkte Instanziierung von TimeEntry und DB-Aufrufe ohne strukturierte Zwischenschicht.
    OOP/MVC-Sinn: Ein Service orchestriert den Use Case und setzt die strengen Architekturgrenzen (Domain vs Persistence) durch.
    """
    
    def __init__(self):
        self.daily_rules = [BreakTimeRule(), MaxDailyWorkRule()]
        self.weekly_rules = [MaxWeeklyWorkRule()]

    def add_work_day(self, employee: Employee, entry_date: date,
                     morning_start: time, morning_end: time,
                     afternoon_start: Optional[time] = None, 
                     afternoon_end: Optional[time] = None,
                     reference_date: Optional[date] = None) -> tuple[TimeEntry, List[Violation]]:
        """
        Erfasst einen Arbeitstag und prüft die täglichen Verstösse.
        """
        entry = TimeEntry(
            entry_date, morning_start, morning_end, 
            afternoon_start, afternoon_end, reference_date=reference_date or date.today()
        )
        
        violations = []
        for rule in self.daily_rules:
            violations.extend(rule.check(entry))
            
        # Hier würde der Aufruf an das Repository stattfinden, z.B. repository.save(entry)
        return entry, violations

    def evaluate_week(self, employee: Employee, year: int, calendar_week: int, entries: List[TimeEntry]) -> tuple[Workweek, List[Violation]]:
        """
        Baut eine Woche aus Einträgen zusammen und prüft wochenbasierte Verstösse.
        """
        week = Workweek(employee, calendar_week, year)
        for entry in entries:
            week.add_entry(entry)
            
        violations = []
        for rule in self.weekly_rules:
            violations.extend(rule.check(week))
            
        return week, violations

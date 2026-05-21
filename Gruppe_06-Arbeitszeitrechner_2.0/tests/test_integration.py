import pytest
from datetime import date, time
from src.domain.services import TimeTrackingService
from src.persistence.repositories.time_entry_repository import TimeEntryRepository
from src.persistence.repositories.employee_repository import EmployeeRepository

class IntegrationRepo:
    def __init__(self, entry_repo):
        self.entry_repo = entry_repo
    
    def save(self, entry):
        return self.entry_repo.save(entry, employee_id=1, calendar_week=17, year=2026)
        
    def find_entries_for_week(self, emp_id, year, cal_week):
        return self.entry_repo.find_entries_for_week(emp_id, year, cal_week)

def test_integration_add_valid_work_day_saves_entry(seeded_db):
    """Integration-Test 1: Korrekter Start-Stopp block löst keine Verstösse aus und wird persistiert."""
    employee_repo = EmployeeRepository(seeded_db)
    time_entry_repo = TimeEntryRepository(seeded_db)
    service = TimeTrackingService(repository=IntegrationRepo(time_entry_repo))
    
    employee = employee_repo.find_by_id(1)
    
    entry, violations = service.add_work_day(
        employee=employee,
        entry_date=date(2026, 4, 20),
        morning_start=time(8, 0),
        morning_end=time(12, 0),
        reference_date=date(2026, 4, 25)
    )
    
    assert entry.id is not None
    assert len(violations) == 0

def test_integration_add_work_day_with_overtime_triggers_violation(seeded_db):
    """Integration-Test 2: Überstunden ohne Pause lösen Violation in der Application Facade aus."""
    employee_repo = EmployeeRepository(seeded_db)
    time_entry_repo = TimeEntryRepository(seeded_db)
    service = TimeTrackingService(repository=IntegrationRepo(time_entry_repo))
    
    employee = employee_repo.find_by_id(1)
    
    entry, violations = service.add_work_day(
        employee=employee,
        entry_date=date(2026, 4, 21),
        morning_start=time(8, 0),
        morning_end=time(14, 30), # > 5.5h ohne Pause
        reference_date=date(2026, 4, 25)
    )
    
    assert entry.id is not None
    assert len(violations) > 0
    assert violations[0].type == "Pausenregelung"

def test_integration_evaluate_week_summary(seeded_db):
    """Integration-Test 3: Fetch Summary aus dem Store liefert korrekt aggregierte Woche."""
    employee_repo = EmployeeRepository(seeded_db)
    time_entry_repo = TimeEntryRepository(seeded_db)
    service = TimeTrackingService(repository=IntegrationRepo(time_entry_repo))
    
    employee = employee_repo.find_by_id(1)
    
    # Store Mon
    service.add_work_day(
        employee=employee,
        entry_date=date(2026, 4, 20),
        morning_start=time(8, 0), morning_end=time(12, 0),
        reference_date=date(2026, 4, 25)
    )
    
    # Store Tue
    service.add_work_day(
        employee=employee,
        entry_date=date(2026, 4, 21),
        morning_start=time(8, 0), morning_end=time(10, 0),
        reference_date=date(2026, 4, 25)
    )
    
    summary = service.get_employee_weekly_summary(employee, 2026, 17)
    
    assert summary["total_hours"] == 6.0 # 4h + 2h
    assert len(summary["entries"]) == 2
    assert summary["overtime"] < 0 

import pytest
from datetime import date, time
from src.persistence.repositories.employee_repository import EmployeeRepository
from src.persistence.repositories.time_entry_repository import TimeEntryRepository
from src.domain.users import Employee
from src.domain.time_tracking import TimeEntry

def test_employee_repository_saves_and_retrieves(db):
    """DB-Test 1: Employee wird gespeichert und erfolgreich geladen."""
    repo = EmployeeRepository(db)
    emp = Employee(first_name="John", last_name="Doe", email="john@test.ch", employment_percentage=80.0)
    
    saved_emp = repo.save(emp)
    
    assert saved_emp.id is not None
    assert saved_emp.email == "john@test.ch"
    
    loaded_emp = repo.find_by_id(int(saved_emp.id))
    assert loaded_emp is not None
    assert loaded_emp.first_name == "John"
    assert loaded_emp.employment_percentage == 80.0

def test_time_entry_repository_saves_and_retrieves(seeded_db):
    """DB-Test 2: TimeEntry wird mit Abhängigkeit auf Mitarbeiter gespeichert."""
    repo = TimeEntryRepository(seeded_db)
    
    entry = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0), time(13, 0), time(17, 0))
    saved_entry = repo.save(entry, employee_id=1, calendar_week=17, year=2026)
    
    assert saved_entry is not None
    
    loaded_entry = repo.find_by_date(1, date(2026, 4, 20))
    assert loaded_entry is not None
    assert loaded_entry.date == date(2026, 4, 20)

def test_time_entry_repository_finds_entries_for_week(seeded_db):
    """DB-Test 3: Query auf Wochenbasis liefert gefilterte Resultate."""
    repo = TimeEntryRepository(seeded_db)
    
    entry1 = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0))
    entry2 = TimeEntry(date(2026, 4, 21), time(8, 0), time(12, 0))
    entry3_other_week = TimeEntry(date(2026, 5, 20), time(8, 0), time(12, 0))
    
    repo.save(entry1, employee_id=1, calendar_week=17, year=2026)
    repo.save(entry2, employee_id=1, calendar_week=17, year=2026)
    # entry 3 goes to week 21
    repo.save(entry3_other_week, employee_id=1, calendar_week=21, year=2026)
    
    week_entries = repo.find_entries_for_week(employee_id=1, year=2026, calendar_week=17)
    
    # Assert only the two entries in week 17 are retrieved
    assert len(week_entries) == 2

import pytest
from datetime import date, time, timedelta

from src.domain.users import Employee
from src.domain.time_tracking import TimeEntry, BreakTimeRule, MaxDailyWorkRule

@pytest.fixture
def employee():
    return Employee("Max", "Test", "test@test.ch", 100.0)

def test_invalid_time_order():
    """Unit-Test 1: Endzeit vor Startzeit (Expected: ValueError)."""
    with pytest.raises(ValueError, match="Endzeit muss nach der Morgen-Startzeit liegen"):
        TimeEntry(date(2026, 4, 20), morning_start=time(12, 0), morning_end=time(8, 0))

def test_future_date_rejected():
    """Unit-Test 2: Zeit in der Zukunft wird abgelehnt."""
    with pytest.raises(ValueError, match="keine Arbeitszeiten für die Zukunft"):
        TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0), reference_date=date(2026, 4, 19))

def test_incomplete_afternoon_block():
    """Unit-Test 3: Nachmittag nicht vollständig ausgefüllt."""
    with pytest.raises(ValueError, match="Nachmittagsblock muss vollständig sein"):
        TimeEntry(date(2026, 4, 20), morning_start=time(8, 0), morning_end=time(12, 0), afternoon_start=time(13, 0))

def test_break_time_rule_violation():
    """Unit-Test 4: Tagesarbeitszeit lang ohne Pause löst Violation aus."""
    entry = TimeEntry(date(2026, 4, 20), time(8, 0), time(14, 0), reference_date=date(2026, 4, 21)) # 6 hours, no break
    rule = BreakTimeRule()
    violations = rule.check(entry)
    assert len(violations) == 1
    assert violations[0].type == "Pausenregelung"

def test_max_daily_work_rule_violation():
    """Unit-Test 5: Tagesarbeitszeit zu lang (> 14h), löst Violation aus."""
    entry = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0), time(12, 10), time(23, 10), reference_date=date(2026, 4, 21))
    rule = MaxDailyWorkRule()
    violations = rule.check(entry)
    assert len(violations) == 1
    assert violations[0].type == "Maximalarbeitszeit"

def test_employee_validates_employment_percentage():
    """Unit-Test 6: Ungültige Beschäftigungsgrade lösen Exception aus."""
    with pytest.raises(ValueError):
        Employee("Test", "User", "test@test.com", -10.0)
    with pytest.raises(ValueError):
        Employee("Test", "User", "test@test.com", 150.0)
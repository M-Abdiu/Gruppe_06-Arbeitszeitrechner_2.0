import pytest
from datetime import date, time, timedelta

from src.domain.users import Employee
from src.domain.time_tracking import TimeEntry, Workweek, BreakTimeRule, MaxDailyWorkRule, MaxWeeklyWorkRule

@pytest.fixture
def employee():
    return Employee("Max", "Test", "test@test.ch", 100.0)

def test_invalid_time_order():
    """Endzeit vor Startzeit (Expected: ValueError)."""
    with pytest.raises(ValueError, match="Endzeit muss nach der Morgen-Startzeit liegen"):
        TimeEntry(date(2026, 4, 20), morning_start=time(12, 0), morning_end=time(8, 0))

def test_future_date_rejected():
    """Zeit in der Zukunft wird abgelehnt."""
    with pytest.raises(ValueError, match="keine Arbeitszeiten für die Zukunft"):
        # date.today() is default reference, but we pass reference_date = yesterday to simulate
        TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0), reference_date=date(2026, 4, 19))

def test_incomplete_afternoon_block():
    """Nachmittag nicht vollständig."""
    with pytest.raises(ValueError, match="Nachmittagsblock muss vollständig sein"):
        TimeEntry(date(2026, 4, 20), morning_start=time(8, 0), morning_end=time(12, 0), afternoon_start=time(13, 0))

def test_no_afternoon_block():
    """Nachmittag fehlt komplett."""
    entry = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0), afternoon_start=None, afternoon_end=None, reference_date=date(2026, 4, 21))
    assert entry.calculate_work_hours() == timedelta(hours=4)
    assert entry.calculate_break_time() == timedelta(0)

def test_break_time_rule_violation():
    """Tagesarbeitszeit zu lang ohne Pause, löst korrekte Violation aus."""
    entry = TimeEntry(date(2026, 4, 20), time(8, 0), time(14, 0), reference_date=date(2026, 4, 21)) # 6 hours, no break
    rule = BreakTimeRule()
    violations = rule.check(entry)
    assert len(violations) == 1
    assert violations[0].type == "Pausenregelung"

def test_max_daily_work_rule_violation():
    """Tagesarbeitszeit zu lang (> 14h), löst korrekte Violation aus."""
    # 8-12 and 12-23 (15 hours total)
    entry = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0), time(12, 10), time(23, 10), reference_date=date(2026, 4, 21))
    rule = MaxDailyWorkRule()
    violations = rule.check(entry)
    assert len(violations) == 1
    assert violations[0].type == "Maximalarbeitszeit"

def test_workweek_duplicate_day(employee):
    """Doppelte Einträge für denselben Tag in der Workweek werden abgelehnt."""
    week = Workweek(employee, 17, 2026)
    entry1 = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0), reference_date=date(2026, 4, 21))
    entry2 = TimeEntry(date(2026, 4, 20), time(13, 0), time(17, 0), reference_date=date(2026, 4, 21))
    
    week.add_entry(entry1)
    with pytest.raises(ValueError, match="existiert bereits in dieser Woche"):
        week.add_entry(entry2)

def test_workweek_target_hours_part_time():
    """Wochenstunden unter/über Soll (mit einem 50% Employee)."""
    employee_pt = Employee("Teil", "Zeit", "teil@zeit.ch", 50.0) # 21h Soll
    week = Workweek(employee_pt, 17, 2026)
    
    # 24h arbeiten
    week.add_entry(TimeEntry(date(2026, 4, 20), time(8, 0), time(16, 0), reference_date=date(2026, 4, 21)))
    week.add_entry(TimeEntry(date(2026, 4, 21), time(8, 0), time(16, 0), reference_date=date(2026, 4, 22)))
    week.add_entry(TimeEntry(date(2026, 4, 22), time(8, 0), time(16, 0), reference_date=date(2026, 4, 23)))
    
    assert week.calculate_target_hours() == timedelta(hours=21)
    assert week.get_total_hours() == timedelta(hours=24)
    assert week.calculate_overtime() == timedelta(hours=3)

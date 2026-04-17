import unittest
import pytest
from datetime import date, time, timedelta
from src.domain.users import Employee
from src.domain.time_tracking import TimeEntry, Workweek

class TestDomainRules(unittest.TestCase):

    def test_employee_validates_employment_percentage(self):
        with self.assertRaises(ValueError):
            Employee("Test", "User", "test@test.com", -10.0)
        with self.assertRaises(ValueError):
            Employee("Test", "User", "test@test.com", 150.0)

    def test_time_entry_violation_exact_threshold(self):
        # 8:00 bis 13:30 sind EXAKT 5.5 Stunden. Gemäss Regel "> 5.5" dürfte KEIN Verstoss vorliegen.
        entry = TimeEntry(date(2026, 4, 20), time(8, 0), time(13, 30))
        violations = entry.get_daily_violations()
        self.assertEqual(len(violations), 0)

    def test_time_entry_zero_break(self):
        # 08:00 - 12:00 und direkt 12:00 - 17:00
        # Die aktuelle Validierung lässt das durch, aber es wertet die Pause als 0h.
        entry = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0), time(12, 0), time(17, 0))
        violations = entry.get_daily_violations()
        
        self.assertEqual(entry.calculate_break_time(), timedelta(0))
        self.assertTrue(len(violations) > 0)  # Erwartet zwingend einen Verstoss wegen fehlender Pause

    def test_future_date_not_allowed(self):
        future_date = date.today() + timedelta(days=5)
        with self.assertRaises(ValueError) as context:
            TimeEntry(future_date, time(8, 0), time(12, 0))
        self.assertTrue("Zukunft erfasst werden" in str(context.exception))

    def test_workweek_iso_calendar_edge_case(self):
        standard_employee = Employee("Test", "User", "test@test.com", 100.0)
        # Der 1. Januar 2027 ist ein Freitag.
        # ISO-Kalender sagt: Jahr 2026, Woche 53.
        target_date = date(2027, 1, 1)
        iso_year, iso_week, _ = target_date.isocalendar()
        
        week = Workweek(standard_employee, iso_week, iso_year) # Workweek für 2026 / KW 53
        entry = TimeEntry(target_date, time(8, 0), time(12, 0))
        
        # Wenn die Prüfung in Workweek starr entry_year != self.year (Gregorianisch) prüft, crasht es hier.
        week.add_entry(entry) 
        self.assertEqual(len(week.entries), 1)

if __name__ == '__main__':
    unittest.main()
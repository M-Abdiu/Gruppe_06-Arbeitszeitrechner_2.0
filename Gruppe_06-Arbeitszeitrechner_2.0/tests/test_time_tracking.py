import unittest
from datetime import date, time, timedelta
from src.domain.users import Employee
from src.domain.time_tracking import TimeEntry, Workweek
from src.domain.violations import Violation

class TestTimeTracking(unittest.TestCase):

    def setUp(self):
        self.employee = Employee("Max", "Test", "test@test.ch", 100.0)

    def test_invalid_time_order(self):
        with self.assertRaises(ValueError):
            TimeEntry(date(2026, 4, 20), morning_start=time(12, 0), morning_end=time(8, 0))

    def test_calculate_work_hours(self):
        entry = TimeEntry(
            date(2026, 4, 20), 
            morning_start=time(8, 15), morning_end=time(12, 0),
            afternoon_start=time(13, 0), afternoon_end=time(17, 30)
        )
        self.assertEqual(entry.calculate_work_hours(), timedelta(hours=8, minutes=15))

    def test_workweek_invariant_calendar_week(self):
        week = Workweek(self.employee, 17, 2026)
        # 20. April 2026 is week 17
        entry_valid = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0))
        week.add_entry(entry_valid)
        
        # 13. April 2026 is week 16
        entry_invalid = TimeEntry(date(2026, 4, 13), time(8, 0), time(12, 0))
        with self.assertRaises(ValueError):
            week.add_entry(entry_invalid)

    def test_workweek_duplicate_day(self):
        week = Workweek(self.employee, 17, 2026)
        entry1 = TimeEntry(date(2026, 4, 20), time(8, 0), time(12, 0))
        entry2 = TimeEntry(date(2026, 4, 20), time(13, 0), time(17, 0))
        
        week.add_entry(entry1)
        with self.assertRaises(ValueError):
            week.add_entry(entry2)

if __name__ == '__main__':
    unittest.main()

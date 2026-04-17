import unittest
from src.domain.users import User, Employee, Admin

class TestUsers(unittest.TestCase):

    def test_cannot_instantiate_abstract_user(self):
        with self.assertRaises(TypeError):
            User("Max", "Test", "test@test.ch", "Employee")

    def test_employee_target_hours(self):
        emp_100 = Employee("Max", "Test", "t@t.ch", 100.0)
        self.assertEqual(emp_100.get_weekly_target_hours(), 42.0)
        
        emp_80 = Employee("Susi", "Test", "t@t.ch", 80.0)
        self.assertEqual(emp_80.get_weekly_target_hours(), 33.6)

    def test_custom_entity_id(self):
        custom_id = "1234-abcd"
        admin = Admin("Boss", "Boss", "boss@test.ch", entity_id=custom_id)
        self.assertEqual(admin.id, custom_id)

if __name__ == '__main__':
    unittest.main()

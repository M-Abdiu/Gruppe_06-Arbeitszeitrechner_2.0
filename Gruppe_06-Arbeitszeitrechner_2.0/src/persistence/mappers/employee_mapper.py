"""
Mapper für Employee-Konvertierung zwischen Domain und Persistence Layer.
Separiert die Datentransformation von der Business Logic.
"""
from typing import Optional
from src.domain.users import Employee
from src.persistence.models import User as DBUser


class EmployeeMapper:
    """Konvertiert zwischen Domain-Employee und DB-User."""
    
    @staticmethod
    def to_db(employee: Employee) -> DBUser:
        """Domain Model → Database Model"""
        return DBUser(
            pk_user_id=None,  # Auto-generate by DB
            username=employee.email.split('@')[0],  # Ableitung aus Email
            Vorname=employee.first_name,
            Nachname=employee.last_name,
            Email=employee.email,
            Passwort="",  # TODO: Passwort-Hashing implementieren
            IsAAdmin=employee.has_admin_privileges(),
            Pensum=int(employee.employment_percentage),
        )
    
    @staticmethod
    def to_domain(db_user: DBUser) -> Employee:
        """Database Model → Domain Model"""
        return Employee(
            first_name=db_user.Vorname,
            last_name=db_user.Nachname,
            email=db_user.Email,
            employment_percentage=float(db_user.Pensum),
            entity_id=str(db_user.pk_user_id),
        )

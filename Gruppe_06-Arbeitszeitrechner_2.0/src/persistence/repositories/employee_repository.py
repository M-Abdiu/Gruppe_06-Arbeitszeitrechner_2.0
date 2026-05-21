"""
Repository für Employee/User-Persistierung.
Ermöglicht Speicherung und Abfrage von Mitrabeitern/Administratoren.
"""
from typing import Optional, List
from sqlmodel import Session, select
from src.domain.users import Employee, Admin
from src.persistence.models import User as DBUser
from src.persistence.mappers import EmployeeMapper


class EmployeeRepository:
    """Persistiert und lädt Employee-Objekte aus der Datenbank."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, employee: Employee) -> Employee:
        """Speichert einen Employee in die DB."""
        db_user = EmployeeMapper.to_db(employee)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return EmployeeMapper.to_domain(db_user)
    
    def find_by_id(self, employee_id: int) -> Optional[Employee]:
        """Lädt einen Employee anhand der ID."""
        db_user = self.session.exec(
            select(DBUser).filter(DBUser.pk_user_id == employee_id)
        ).first()
        if not db_user:
            return None
        
        # Instanziiere basierend auf IsAdmin Flag
        if db_user.IsAAdmin:
            return Admin(
                first_name=db_user.Vorname,
                last_name=db_user.Nachname,
                email=db_user.Email,
                entity_id=str(db_user.pk_user_id),
            )
        else:
            return Employee(
                first_name=db_user.Vorname,
                last_name=db_user.Nachname,
                email=db_user.Email,
                employment_percentage=float(db_user.Pensum),
                entity_id=str(db_user.pk_user_id),
            )
    
    def find_by_email(self, email: str) -> Optional[Employee]:
        """Lädt einen Employee anhand der Email."""
        db_user = self.session.exec(
            select(DBUser).filter(DBUser.Email == email)
        ).first()
        return EmployeeMapper.to_domain(db_user) if db_user else None
    
    def find_all_employees(self) -> List[Employee]:
        """Lädt alle Mitarbeiter (Employees, nicht Admins)."""
        db_users = self.session.exec(
            select(DBUser).filter(DBUser.IsAAdmin == False)
        ).all()
        return [EmployeeMapper.to_domain(db_user) for db_user in db_users]
    
    def delete(self, employee_id: int) -> bool:
        """Löscht einen Employee."""
        db_user = self.session.exec(
            select(DBUser).filter(DBUser.pk_user_id == employee_id)
        ).first()
        if db_user:
            self.session.delete(db_user)
            self.session.commit()
            return True
        return False

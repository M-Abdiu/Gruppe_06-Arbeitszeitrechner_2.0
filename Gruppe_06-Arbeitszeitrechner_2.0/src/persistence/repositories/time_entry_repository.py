"""
Repository für TimeEntry-Persistierung.
Bildet eine Abstrakts-Schicht zwischen Domain und Database.
"""
from datetime import date
from typing import Optional, List
from sqlmodel import Session, select
from src.domain.time_tracking import TimeEntry
from src.persistence.models import TimeEntry as DBTimeEntry
from src.persistence.mappers import TimeEntryMapper


class TimeEntryRepository:
    """Persistiert und lädt TimeEntry-Objekte aus der Datenbank."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, entry: TimeEntry, employee_id: int, calendar_week: int, year: int) -> TimeEntry:
        """
        Speichert einen TimeEntry in die DB.
        
        :param entry: Domain TimeEntry
        :param employee_id: ID des Mitarbeiters
        :param calendar_week: Kalenderwoche
        :param year: Jahr
        :return: Gespeicherter TimeEntry mit ggf. generierter ID
        """
        db_entry = TimeEntryMapper.to_db(entry, employee_id, calendar_week, year)
        self.session.add(db_entry)
        self.session.commit()
        self.session.refresh(db_entry)
        return TimeEntryMapper.to_domain(db_entry)
    
    def find_by_date(self, employee_id: int, entry_date: date) -> Optional[TimeEntry]:
        """Lädt einen TimeEntry für ein bestimmtes Datum."""
        db_entry = self.session.exec(
            select(DBTimeEntry)
            .filter(DBTimeEntry.fk_user_id == employee_id)
            .filter(DBTimeEntry.Tag == entry_date.isoformat())
        ).first()
        return TimeEntryMapper.to_domain(db_entry) if db_entry else None
    
    def find_entries_for_week(self, employee_id: int, year: int, calendar_week: int) -> List[TimeEntry]:
        """Lädt alle TimeEntries einer Woche für einen Mitarbeiter."""
        db_entries = self.session.exec(
            select(DBTimeEntry)
            .filter(DBTimeEntry.fk_user_id == employee_id)
            .filter(DBTimeEntry.Jahr == year)
            .filter(DBTimeEntry.Kalenderwoche == calendar_week)
        ).all()
        return [TimeEntryMapper.to_domain(db_entry) for db_entry in db_entries]
    
    def delete(self, employee_id: int, entry_date: date) -> bool:
        """Löscht einen TimeEntry."""
        db_entry = self.find_by_date(employee_id, entry_date)
        if db_entry:
            self.session.delete(db_entry)
            self.session.commit()
            return True
        return False

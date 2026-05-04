"""
Mapper für TimeEntry-Konvertierung zwischen Domain und Persistence Layer.
Behandelt die komplexe Konvertierung von Zeit-Objekten (time → float).
"""
from datetime import date, time
from src.domain.time_tracking import TimeEntry
from src.persistence.models import TimeEntry as DBTimeEntry


class TimeEntryMapper:
    """Konvertiert zwischen Domain-TimeEntry und DB-TimeEntry."""
    
    @staticmethod
    def time_to_decimal(t: time) -> float:
        """Konvertiert time(12, 30) → 12.5"""
        return t.hour + t.minute / 60.0
    
    @staticmethod
    def decimal_to_time(decimal: float) -> time:
        """Konvertiert 12.5 → time(12, 30)"""
        hours = int(decimal)
        minutes = int(round((decimal - hours) * 60))
        # Sicherheit gegen overflow
        if minutes >= 60:
            hours += 1
            minutes = 0
        return time(hours % 24, minutes)
    
    @staticmethod
    def to_db(entry: TimeEntry, employee_id: int, calendar_week: int, year: int) -> DBTimeEntry:
        """Domain Model → Database Model"""
        db_entry = DBTimeEntry(
            pk_TimeEntry_id=None,  # Auto-generate
            fk_user_id=employee_id,
            Kalenderwoche=calendar_week,
            Jahr=year,
            Tag=entry.date.strftime("%Y-%m-%d"),
            MorgenBeginn=TimeEntryMapper.time_to_decimal(entry.morning_start),
            MorgenStop=TimeEntryMapper.time_to_decimal(entry.morning_end),
            NachmittagBeginn=TimeEntryMapper.time_to_decimal(entry.afternoon_start) if entry.afternoon_start else 0.0,
            NachmittagStop=TimeEntryMapper.time_to_decimal(entry.afternoon_end) if entry.afternoon_end else 0.0,
        )
        return db_entry
    
    @staticmethod
    def to_domain(db_entry: DBTimeEntry) -> TimeEntry:
        """Database Model → Domain Model"""
        entry_date = date.fromisoformat(db_entry.Tag)
        
        morning_start = TimeEntryMapper.decimal_to_time(db_entry.MorgenBeginn)
        morning_end = TimeEntryMapper.decimal_to_time(db_entry.MorgenStop)
        afternoon_start = TimeEntryMapper.decimal_to_time(db_entry.NachmittagBeginn) if db_entry.NachmittagBeginn > 0.0 else None
        afternoon_end = TimeEntryMapper.decimal_to_time(db_entry.NachmittagStop) if db_entry.NachmittagStop > 0.0 else None
        
        return TimeEntry(
            entry_date=entry_date,
            morning_start=morning_start,
            morning_end=morning_end,
            afternoon_start=afternoon_start,
            afternoon_end=afternoon_end,
        )

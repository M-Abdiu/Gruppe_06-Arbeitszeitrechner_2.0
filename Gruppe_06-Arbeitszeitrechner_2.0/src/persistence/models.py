from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    
    pk_user_id: int = Field(default=None, primary_key=True)
    username: str
    Vorname: str
    Nachname: str
    Email: str
    Passwort:  str 
    IsAAdmin: bool
    Pensum: int = Field(default=100)
    

class Violation (SQLModel, table=True):
    
    pk_violation_id: int = Field(default=None, primary_key=True)
    fk_TimeEntry_id: int = Field(default=None, foreign_key="TimeEntry.pk_TimeEntry_id")
    type: str
    
class TimeEntry(SQLModel, table=True):
    
    pk_TimeEntry_id: int = Field(default=None, primary_key=True)
    fk_user_id: int = Field(default=None, foreign_key="user.pk_user_id")
    Kalenderwoche: int
    Jahr: int
    Tag: str
    MorgenBeginn: float
    MorgenStop: float
    NachmittagBeginn:  float 
    NachmittagStop: float    

from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    
    pk_user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    Vorname: str
    Nachname: str
    Email: str
    Passwort:  str 
    IsAAdmin: bool
    
    

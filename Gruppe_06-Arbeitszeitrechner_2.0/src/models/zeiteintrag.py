from typing import Optional
from sqlmodel import Field, SQLModel

class Zeiteintrag(SQLModel, table=True):
    
    pk_zeiteintrag_id: Optional[int] = Field(default=None, primary_key=True)
    fk_user_id: Optional[int] = Field(default=None, foreign_key="user.pk_user_id")
    Kalenderwoche: int
    Tag: str
    MorgenBeginn: float
    MorgenStop: float
    NachmittagBeginn:  float 
    NachmittagStop: float
    

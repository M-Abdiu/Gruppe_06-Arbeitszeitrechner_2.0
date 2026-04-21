from typing import Optional
from sqlmodel import Field, SQLModel

class Violation (SQLModel, table=True):
    
    pk_violation_id: Optional[int] = Field(default=None, primary_key=True)
    fk_zeiteintrag_id: Optional[int] = Field(default=None, foreign_key="zeiteintrag.pk_zeiteintrag_id")
    type: str
    
    
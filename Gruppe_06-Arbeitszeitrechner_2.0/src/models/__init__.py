from Database import engine, SQLModel
from sqlmodel import Session
from sqlmodel import select
with Session(engine) as session:

    session.commit()
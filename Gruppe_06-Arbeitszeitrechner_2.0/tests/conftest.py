import pytest
from sqlmodel import SQLModel, create_engine, Session
from src.persistence.models import User, TimeEntry, Violation

# In-memory SQLite for testing
@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine

@pytest.fixture(name="db")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="seeded_db")
def seeded_session_fixture(db):
    user1 = User(
        username="mtester",
        Vorname="Max",
        Nachname="Tester",
        Email="max.tester@test.ch",
        Passwort="password",
        IsAAdmin=False,
        Pensum=100
    )
    user2 = User(
        username="admin",
        Vorname="Boss",
        Nachname="Admin",
        Email="boss@test.ch",
        Passwort="password",
        IsAAdmin=True,
        Pensum=100
    )
    db.add(user1)
    db.add(user2)
    db.commit()
    return db

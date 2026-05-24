from sqlmodel import create_engine, SQLModel


engine = create_engine("sqlite:///company.db")


def _migrate_violation_table() -> None:
    """Ergänzt fehlende Violation-Spalten in bestehenden SQLite-Datenbanken."""
    with engine.begin() as connection:
        columns = connection.exec_driver_sql("PRAGMA table_info(violation)").all()
        if not columns:
            return

        existing_columns = {column[1] for column in columns}

        if "message" not in existing_columns:
            connection.exec_driver_sql(
                "ALTER TABLE violation ADD COLUMN message TEXT NOT NULL DEFAULT ''"
            )

        if "violation_date" not in existing_columns:
            connection.exec_driver_sql(
                "ALTER TABLE violation ADD COLUMN violation_date DATE"
            )

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _migrate_violation_table()

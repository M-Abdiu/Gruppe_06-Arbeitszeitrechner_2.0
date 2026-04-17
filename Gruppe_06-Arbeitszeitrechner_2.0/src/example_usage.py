from datetime import date, time
from domain.users import Employee, Admin
from domain.time_tracking import TimeEntry, Workweek

def run_example():
    print("--- Arbeitszeitrechner 2.0: Domain Logik Beispiel ---\n")

    # 1. Mitarbeiter erstellen (80% Pensum)
    employee = Employee(
        first_name="Max", 
        last_name="Mustermann", 
        email="max.mustermann@example.com", 
        employment_percentage=80.0
    )
    
    print(f"Mitarbeiter: {employee.first_name} {employee.last_name} ({employee.role})")
    print(f"Pensum: {employee.employment_percentage}%")
    print(f"Wöchentliche Sollzeit: {employee.get_weekly_target_hours():.1f} Stunden\n")

    # 2. Arbeitswoche erstellen (KW 17)
    workweek = Workweek(employee=employee, calendar_week=17, year=2026)

    # 3. Zeiteinträge erstellen und der Woche hinzufügen
    
    # Montag: Normaler Arbeitstag
    monday = TimeEntry(
        entry_date=date(2026, 4, 20),
        morning_start=time(8, 0), morning_end=time(12, 0),
        afternoon_start=time(13, 0), afternoon_end=time(17, 0)
    )
    workweek.add_entry(monday)

    # Dienstag: Zu lange gearbeitet & zu wenig Pause
    try:
        tuesday = TimeEntry(
            entry_date=date(2026, 4, 21),
            morning_start=time(8, 0), morning_end=time(12, 0),
            afternoon_start=time(12, 10), afternoon_end=time(23, 0)
        )
        workweek.add_entry(tuesday)
    except ValueError as e:
        print(f"Fehler beim Erstellen des Eintrags: {e}")

    # Mittwoch: Nur am Vormittag gearbeitet
    wednesday = TimeEntry(
        entry_date=date(2026, 4, 22),
        morning_start=time(8, 0), morning_end=time(12, 0)
    )
    workweek.add_entry(wednesday)

    # 4. Auswertungen berechnen
    print("--- Wochenauswertung ---")
    total_h = workweek.get_total_hours().total_seconds() / 3600.0
    target_h = workweek.calculate_target_hours().total_seconds() / 3600.0
    overtime_h = workweek.calculate_overtime().total_seconds() / 3600.0
    print(f"Total gearbeitet:      {total_h:.2f} Stunden")
    print(f"Sollzeit (Woche):      {target_h:.2f} Stunden")
    print(f"Aktueller Zeitsaldo:   {overtime_h:.2f} Stunden (Überstunden/Minusstunden)\n")

    # 5. Verstösse prüfen (Violations)
    print("--- Gefundene Regelverstösse ---")
    verstoesse = workweek.get_weekly_violations()
    
    if not verstoesse:
        print("Keine Verstösse gefunden. Alles im grünen Bereich!")
    else:
        for v in verstoesse:
            print(v)

if __name__ == "__main__":
    run_example()

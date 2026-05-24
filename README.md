# Arbeitszeit-Auswertungs Programm

![UI Showcase](Gruppe_06-Arbeitszeitrechner_2.0\docs\ui_showcase.png)

---

This project is intended to:

- Practice the complete process from **application requirements analysis to implementation**
- Apply advanced **Python** concepts in a browser-based application (NiceGUI)
- Demonstrate **data validation**, a clean architecture (presentation / application logic / persistence), and **database access via ORM**
- Produce clean, well-structured, and documented code (incl. tests)
- Prepare students for **teamwork and professional documentation**
- Use this repository as a starting point by importing it into your own GitHub account  
- Work only within your own copy — do not push to the original template  
- Commit regularly to track your progress

---
## 📝 Application Requirements

---

### Problem

Das Problem ist, dass der Vorgesetzte ein File erhält in dem alle Mitarbeiter ihre gestempelten Zeiten eintragen und er muss immer alles manuell berechnen. Er muss berechnen wie lange die Mitarbeiter gearbeitet haben und schauen, ob sie die vertraglichen Rahmenbedingungen verletzt haben. Er möchte eine Übersicht haben über die jeweiligen Mitarbeiter, in der gezeigt wird: Mitarbeiter, Pensum, Ist-Zeit, Soll-Zeit, Differenz-Stunden, Einhaltung der Rahmenbedinungen und falls verletzt, Welche Rahmenbedingung verletzt wurde und dies nicht immer manuell berechnen müssen. Mitarbeiter sollen nun ihre Stunden digital auf der App erfassen und ihre eigenen Stundenauszug sehen können.

---

### Scenario

Der Admin will eine Übersicht über die Stunden haben, welches die wöchentliche Stemplungen der Mitarbeiter beinhaltet. Schlussendlich soll er als Output im Browser , eine Übersicht erhalten in der aufgeführt ist:
- Nachname, Vorname, Pensum
- Effektivstunden
- Soll-Zeit
- Differenz-Zeit
- Pausen-Zeit
- Vertragsbedingungen eingehalten?
- Begründung der Vertrags-Verletzung

Der Admin soll eine Gesamtübersicht erhalten, aber auch die Option haben, individuelle Mitarbeterauszüge nach Kalenderwoche anzuschauen.

Der Mitarbeiter (Employee) soll seine eigenen Arbeitszeiten digital erfassen und verwalten können. Als Output im Browser soll er eine persönliche Übersicht erhalten, in der aufgeführt ist:
- Effektivstunden (Ist-Zeit) pro Woche
- Individuelle Soll-Zeit (basierend auf dem Pensum)
- Differenz-Zeit (Über- oder Minusstunden)
- Einhaltung der Rahmenbedingungen (Pausen- und Maximalarbeitszeiten) inkl. Begründung bei Verstössen

Der Mitarbeiter soll eine detaillierte Ansicht seiner Stundenauszüge pro Kalenderwoche haben und die Möglichkeit besitzen, Arbeitszeiten der aktuellen Woche anzupassen.

---

## User Stories

### 1. Worker: Login
**Als Worker möchte ich, mich einloggen und meine Module sehen basierend auf meiner Berechtigung**

- **Inputs:** username (`str`), password (`str`)
- **Outputs:** none

### 2. Worker: Stundeneintrag
**Als Worker möchte ich, mich einloggen und meine Arbeitsstunden eintragen für eine Kalenderwoche**

**Regeln:**
- Keine Nachtschicht (nur Tagesarbeit).
- Pro Tag maximal 4 Zeitstempel (Morgen-Start, Morgen-Ende, Nachmittag-Start, Nachmittag-Ende).
- Pausen sind auf 15 Minuten festgelegt.

- **Inputs:** entry_date (`date`), morning_start (`time`), morning_end (`time`), afternoon_start (`time | None`), afternoon_end (`time | None`)
- **Outputs:** new entry (`TimeEntry`), rule violations (`list[Violation]`)

### 3. Worker: Stundenübersicht
**Als Worker möchte ich, mich einloggen und meine individuelle Arbeitsstundenauszüge sortiert nach Kalenderwoche und möchte eine detaillierten Auschnitt sehen (Soll-Ist Zeit, Diferenz usw.)**

- **Inputs:** year (`int`), calendar_week (`int`)
- **Outputs:** weekly summary (`Workweek`), entries (`list[TimeEntry]`), rule violations (`list[Violation]`)

### 4. Worker: Stundenanpassung
**Als Worker möchte ich, mich einloggen und meine Arbeitsstunden der jetzigen Kalenderwoche modifizieren**

- **Inputs:** entry_id (`str`), updated_times (`time`)
- **Outputs:** updated entry (`TimeEntry`), updated violations (`list[Violation]`)

### 5. Worker: Logout
**Als Worker möchte ich, mich ausloggen können.**

- **Inputs:** none
- **Outputs:** none

### 6. Admin: Login
**Als Admin möchte ich, mich einloggen und meine Module sehen basierend auf meiner Berechtigung**

- **Inputs:** username (`str`), password (`str`)
- **Outputs:** none

### 7. Admin: Stundenübersicht
**Als Admin möchte ich, eine Übersicht der Soll-Zeit, Differenz-Zeit, Pensums jedes einzelnen Mitarbeiters erhalten, der bereits Einträge erstellt hat.**

- **Inputs:** year (`int`), calendar_week (`int`)
- **Outputs:** list of summaries (`list[dict]`) matching all users

### 8. Admin: View Violations Menu
**Als Admin möchte ich, eine Angabe erhalten ob die vertraglichen Rahmenbedingungen eingehalten wurden und gegebenenfalls eine Angabe erhalten welche Rahmenbedingung verletzt wurde pro Mitarbeiter.**

- **Inputs:** filter_params (`dict`)
- **Outputs:** list of rule violations (`list[Violation]`) matching all users

### 9. Admin: User Managment Menu 
**Als Admin möchte ich, neue Mitarbeiter erfassen oder entfernen.**

- **Inputs:** first_name (`str`), last_name (`str`), email (`str`), password (`str`), role (`str`), employment_percentage (`float`)
- **Outputs:** newly created user (`Employee | Admin`)

### 10. Admin: Logout
**Als Admin möchte ich, mich ausloggen können.**

- **Inputs:** none
- **Outputs:** none
---

### Use cases

![Use Case Diagramm](Gruppe_06-Arbeitszeitrechner_2.0\docs\architecture-diagrams\Use%20Case%20Diagramm.png)

## Main Use Cases

1. Arbeitszeiten eintragen
2. Arbeitszeiten ändern
3. Eigene Arbeitszeitübersicht anzeigen
4. Arbeitszeiten der Worker überprüfen
5. Regelverletzungen anzeigen und überprüfen
6. Benutzer anlegen
7. Benutzer löschen

### Technical Use Cases

1. Login
2. Logout

**Actors**
- Worker:   ist ein normaler Benutzer der Anwendung. Er kann eigene Arbeitszeiten erfassen, ändern und seine persönliche Übersicht einsehen.
- Admin:    verwaltet die Benutzer und überprüft die erfassten Arbeitszeiten der Worker. Zusätzlich kann der Admin Regelverletzungen einsehen und kontrollieren.

---

### Wireframes / Mockups

> 🚧 Add screenshots of the wireframe mockups you chose to implement.

**Start:**
![Login](Gruppe_06-Arbeitszeitrechner_2.0\docs\MockUp's\LoginMockUp.png)

**Admin Bereich:**
![Admin View](Gruppe_06-Arbeitszeitrechner_2.0\docs\MockUp's\AdminView_MockUp.png)
![Admin User View](Gruppe_06-Arbeitszeitrechner_2.0\docs\MockUp's\AdminUsermanagment_MockUp.png)
![Admin Violation View](Gruppe_06-Arbeitszeitrechner_2.0\docs\MockUp's\AdminViolation_MockUp.png)


**Worker Bereich:**
![Worker Timeentry View](Gruppe_06-Arbeitszeitrechner_2.0\docs\MockUp's\WorkerTimenetryView_MockUp.png)
![Worker Timeentry Overview](Gruppe_06-Arbeitszeitrechner_2.0\docs\MockUp's\WorkerTimenentryOverview_MockUp.png)

**Created with Balasmiq, free trial version**
---

## 🏛️ Architecture

> 🚧 Document the architecture components, relationships, and key design decisions.

### Software Architecture

> 🚧 Insert your UML class diagram(s). Split into multiple diagrams if needed.

![UML Class Diagram](Gruppe_06-Arbeitszeitrechner_2.0\docs\architecture-diagrams\uml_class_architecture.png)

**Layers / components:**
- UI (Presentation Layer): Wir nutzen NiceGUI für das Frontend. Der Browser dient hier als reiner "Thin Client". Er zeigt die Daten nur an und schickt Eingaben ans Backend.
- Service Schicht (Application Logic): Der `TimeTrackingService` ist der zentrale Punkt. Er nimmt die Anfragen der UI entgegen und delegiert sie an die Logik weiter.
- Domain (Kern Logik): Hier liegen die wichtigen Klassen wie `Worker` oder `Workweek`. Alles, was mit der Berechnung von Stunden oder dem Prüfen von Regeln zu tun hat, passiert hier.
- Persistence (Daten): Wir nutzen SQLModel als ORM. Damit speichern wir die Daten sauber in der SQLite Datenbank (`company.db`), ohne manuellen SQL Code schreiben zu müssen.

**Design decisions (examples):**
- Saubere Trennung: Wir haben darauf geachtet, dass die UI keine Business Logik enthält. Die UI ruft lediglich Funktionen wie `add_work_day()` auf. Die Logik für die Gültigkeit von Zeitstempeln oder Pausenregeln liegt allein in der Domain Schicht.
- Adapter in der UI: Funktionen wie `get_weekly_summary` im UI-Modul dienen nur dazu, die Daten aus der Datenbank für den Service passend umzubauen. Das hält den Rest der App sauber und testbar.
- Validierung: Wir trennen strikt zwischen zwei Arten von Prüfungen. Die UI prüft, ob das Format (zum Beispiel HH:MM) stimmt. Die fachliche Prüfung (zum Beispiel ob die Endzeit nach der Startzeit liegt) übernimmt die Business Logik.

**Design patterns used (examples):**
- Schichtenarchitektur / MVC: Jedes Element hat einen festen Platz (Anzeige, Logik oder Datenbank).
- Repository Pattern: Die Datenhaltung ist vom Rest der App entkoppelt.
- Strategy Pattern: Die Arbeitszeitregeln sind so gekapselt, dass man sie bei Bedarf leicht austauschen oder erweitern kann.
- Facade Pattern: Der Service bietet der UI eine einfache Schnittstelle für die komplexen Abläufe im Hintergrund.

---

### 🗄️ Database and ORM

![ER Diagram](Gruppe_06-Arbeitszeitrechner_2.0\docs\architecture-diagrams\ER_Diagram_.png)

**Entities**
User: Represents a person using the app
TimeEntry: One work-timesheet row
Violation: A rule violation tied to a time entry

**Relationships**
One User → many TimeEntry.
Each TimeEntry references one User
One TimeEntry → zero or many Violation.
Each Violation references one TimeEntry

---

## ✅ Project Requirements

---
Each app must meet the following criteria in order to be accepted (see also the official project guidelines PDF on Moodle):

1. Using NiceGUI for building an interactive web app
2. Data validation in the app
3. Using an ORM for database management

---

### 1. Browser-based App (NiceGUI)

Die gesamte Interaktion mit der Zeiterfassung findet über den Browser statt. Wir setzen dabei konsequent auf NiceGUI, um ein reaktives Web-Interface zu bieten.

**Kern-Funktionen der App:**
- Zentrales Login: Eine Einstiegsmaske validiert die Nutzerdaten und leitet Mitarbeitende oder Admins automatisch in ihren jeweiligen Bereich weiter.
- Mitarbeiter Portal: Hier können Arbeitszeiten tabellarisch für zwei Zeitblöcke pro Tag erfasst werden. Die Ansicht lässt sich nach Kalenderwochen und Jahren filtern.
- Persönliche Auswertung: Mitarbeitende sehen eine Übersicht mit Soll- und Ist-Stunden sowie der berechneten Differenz. Verstösse gegen Arbeitsregeln werden in einem einklappbaren Bereich (Accordion) direkt angezeigt.
- Admin Dashboard: Vorgesetzte erhalten eine globale Übersicht über alle Teammitglieder. Sie sehen sofort den Status der aktuellen Woche sowie detaillierte Listen über Regelüberschreitungen wie missachtete Pausenzeiten.

**Architektur Hinweis:**
Der Browser agiert als Thin Client. Das bedeutet, dass die gesamte Logik für die Berechnungen und die Verwaltung der Oberflächen-Zustände auf dem Server innerhalb der NiceGUI Applikation läuft.

---

### 2. Data Validation

Die Anwendung prüft Eingaben auf mehreren Ebenen, um die Datenintegrität sicherzustellen und Fehlermeldungen verständlich auszugeben.

**Validierung in der UI Schicht:**
In der Datei `src/ui/__init__.py` stellen wir sicher, dass nur korrekte Formate verarbeitet werden. Die Funktion `hhmm_to_decimal` prüft zum Beispiel, ob Zeitangaben im Format HH:MM vorliegen und ob die Werte für Stunden und Minuten innerhalb der logischen Grenzen liegen. Auch die Login Felder werden hier auf Vollständigkeit geprüft.

**Fachliche Validierung in der Domain Schicht:**
Innerhalb der `TimeEntry` Klasse in `src/domain/time_tracking.py` findet die logische Prüfung statt. Hier wird unter anderem sichergestellt, dass Endzeiten niemals vor den Startzeiten liegen. Zudem verhindern wir Buchungen in der Zukunft und prüfen, ob Nachmittagsblöcke überschneidungsfrei zum Morgenblock eingetragen wurden.

**Regelbasierte Validierung:**
Durch den Einsatz von Strategy-Klassen (z.B. `BreakTimeRule` oder `MaxDailyWorkRule`), welche durch unseren `TimeTrackingService` zentral ausgeführt werden, prüfen wir automatisiert vertragliche Rahmenbedingungen. Diese sind für unsere Domäne bewusst vereinfacht modelliert: Die tägliche Pause ist auf fix 15 Minuten definiert, zudem wird die maximale Tages- und Wochenarbeitszeit kontrolliert. Nachtschichten sind systematisch ausgeschlossen.


---

### 3. Database Management

Für die Verwaltung der Daten nutzen wir SQLModel als modernem Object Relational Mapper (ORM). Die Definitionen befinden sich in `src/persistence/models.py`.

**Datenmodell und Relationen:**
- User Modell: Speichert alle Informationen zu den Mitarbeitenden inklusive ihrer Rollen (Admin oder Worker) und des jeweiligen Beschäftigungsgrads für die Sollzeit Berechnung.
- TimeEntry Modell: Dieser Teil bildet die täglichen Arbeitsstempel ab. Über den Fremdschlüssel `fk_user_id` ist jeder Eintrag fest mit einem Benutzer verknüpft. Die Zeiten werden zur besseren Berechenbarkeit als Float Werte gespeichert.
- Violation Modell: Hier werden spezifische Regelverstösse dokumentiert. Dieses Modell ist über den Fremdschlüssel `fk_TimeEntry_id` direkt mit dem entsprechenden Arbeitstag verknüpft, an dem der Fehler aufgetreten ist.

Durch den Einsatz von SQLModel können wir komplexe Abfragen und Verknüpfungen direkt in Python schreiben, was den Code wartbar und sicher gegen SQL Injektionen macht.

---

## ⚙️ Implementation

---

### Technology

- Python 3.x
- Environment: GitHub Codespaces
- External libraries: nicegui, sqlmodel, sqlalchemy, reportlab, python-dotenv, pytest, tzdata

---

### 📂 Repository Structure

```text
Workspace root/
├─ .github/
├─ .nicegui/
├─ company.db
├─ README.md
├─ requirements.txt
└─ Gruppe_06-Arbeitszeitrechner_2.0/
   ├─ docs/
   │  └─ architecture-diagrams/
   │     └─ ER_Diagram_.png
   ├─ src/
   │  ├─ data_access/
   │  │  └─ Database.py
   │  ├─ domain/
   │  │  ├─ __init__.py
   │  │  ├─ config.py
   │  │  ├─ services.py
   │  │  ├─ time_tracking.py
   │  │  ├─ users.py
   │  │  └─ violations.py
   │  ├─ persistence/
   │  │  ├─ __init__.py
   │  │  ├─ models.py
   │  │  ├─ mappers/
   │  │  │  ├─ __init__.py
   │  │  │  ├─ employee_mapper.py
   │  │  │  └─ time_entry_mapper.py
   │  │  └─ repositories/
   │  │     ├─ __init__.py
   │  │     ├─ employee_repository.py
   │  │     └─ time_entry_repository.py
   │  ├─ ui/
   │  │  └─ __init__.py
   │  └─ main.py
   └─ tests/
      ├─ conftest.py
      ├─ test_db.py
      ├─ test_integration.py
      └─ test_time_tracking.py
```

---

### How to Run


### 1. Project Setup
- Python 3.13 (or the course version) is required
- Create and activate a virtual environment:
   - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```
   - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\Activate
      ```
- Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Configuration
Die Applikation nutzt eine lokale SQLite Datenbank (`company.db`). Es ist keine zusätzliche Konfiguration von Umgebungsvariablen oder `.env` Dateien notwendig. Die Datenbank wird beim ersten Start automatisch initialisiert.

### 3. Launch
Starte die NiceGUI App mit dem folgenden Befehl:
```bash
python -m src.main
```
Die Applikation öffnet sich daraufhin automatisch in deinem Standardbrowser unter `http://localhost:8080/`. Falls dies nicht geschieht, klicke auf den Link in der Konsole.


### 4. Usage (Step-by-Step)
Nach dem Start der Anwendung können sich Mitarbeitende und Admins mit ihren jeweiligen Zugangsdaten anmelden. Die Anwendung bietet spezifische Funktionen für zwei Nutzerrollen:

**Als Worker (Mitarbeiter):**
-   **Login Daten:** Benutzername: `berisha`, Passwort: `1234`
-   Logge dich ein und navigiere zum Bereich **Stunden erfassen**.
-   Wähle die gewünschte Kalenderwoche sowie das Jahr aus.
-   Trage deine Arbeitszeiten für den Vormittags- und Nachmittagsblock im Format `HH:MM` ein und klicke auf Speichern.
-   Kontrolliere im Tab **Meine Übersicht** deine berechneten Ist-Stunden, die Differenz zur Soll-Zeit sowie mögliche Hinweise auf Regelverstöße.


**Als Admin:**
-   **Login Daten:** Benutzername: `admin01`, Passwort: `1234`
-   **Team Kontrolle:** Überprüfe in der zentralen **Übersicht** die geleisteten Soll- und Ist-Stunden des gesamten Teams.
-   **Verstösse prüfen:** Wechsle in den Tab **Verstösse**, um gezielt einzusehen, welche Mitarbeitenden gegen gesetzliche Vorgaben wie Pausenregeln oder Maximalarbeitszeit verstoßen haben.
-   **Benutzerverwaltung:** Nutze diesen Bereich, um die Personalien der Mitarbeitenden einzusehen, Beschäftigungsgrade (Pensen) zu verwalten oder bei Bedarf Accounts aus dem System zu entfernen.


---

## 🧪 Testing


**Tests ausführen:**
Wir nutzen `pytest` als unser Testing Framework. Wenn du Probleme hast, die Tests auszuführen (z.B. `ModuleNotFoundError: No module named 'src'`), liegt das am fehlenden Python-Pfad (`PYTHONPATH`). 

Um die Tests in **PowerShell** auf Windows erfolgreich auszuführen, kopiere diese zwei Zeilen nacheinander in dein Terminal (stelle sicher, dass du dich im ersten Hauptordner befindest):

```powershell
cd "Gruppe_06-Arbeitszeitrechner_2.0"
$env:PYTHONPATH="."; python -m pytest tests/
```

**Test-Zusammenstellung:**
- Insgesamt 12 Tests
- 6 Unit-Tests: Startzeit vor Endzeit, Daten in der Zukunft, unvollständige Nachmittagsblöcke, Pausenregeln, maximale Arbeitszeit pro Tag, Begrenzungen beim Beschäftigungsgrad (Pensum).
- 3 DB-Tests: Employee Speicherung und ID-Abruf, TimeEntry Persistenz inkl. Fremdschlüssel, abfragen von Wocheneinträgen via Repository.
- 3 Integration-Tests: Validierung von Arbeitstagen ohne Verstoss, Erkennen von Überstunden über das Service Facade, Berechnen und Abrufen wöchentlicher Auswertungen über die DB und Geschäftslogik.

### Dokumentierte Testfälle

1. **Test case ID:** TC_001
2. **Test case title/description:** Unit-Test: Endzeit vor Startzeit (Invalid time order)
3. **Preconditions:** Domain-Modell `TimeEntry` involviert.
4. **Test steps:** Erstelle ein `TimeEntry` bei dem eine Endzeit vor der dazu passenden Startzeit liegt.
5. **Test data/input:** Morgen Start: 12:00 Uhr, Morgen Ende: 08:00 Uhr.
6. **Expected result:** Das Modell fängt die logische Unstimmigkeit ab und wirft einen `ValueError`.
7. **Actual result:** Ein `ValueError` mit entsprechendem Text wird geworfen.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_invalid_time_order`.

---

1. **Test case ID:** TC_002
2. **Test case title/description:** Unit-Test: Zeitstempel in der Zukunft abweisen
3. **Preconditions:** Domain-Modell `TimeEntry` involviert.
4. **Test steps:** Versuche einen Tag in der Zukunft (bezogen auf das `reference_date`) anzulegen.
5. **Test data/input:** Arbeitsdatum: 2026-04-20, Referenzdatum: 2026-04-19.
6. **Expected result:** Es sind keine Stempelungen in der Zukunft erlaubt (`ValueError`).
7. **Actual result:** `ValueError` wird mit korrektem Match abgefangen.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_future_date_rejected`.

---

1. **Test case ID:** TC_003
2. **Test case title/description:** Unit-Test: Unvollständiger Nachmittagsblock
3. **Preconditions:** Domain-Modell `TimeEntry` involviert.
4. **Test steps:** Eine Startzeit für den Nachmittag übergeben, aber keine Endzeit angeben.
5. **Test data/input:** Morgen: 08:00-12:00, Nachmittag Start: 13:00, Ende: None.
6. **Expected result:** `ValueError`, da ein Block komplett gefüllt sein muss.
7. **Actual result:** Korrekte Exception wird aufgrund fehlendem Paar getriggert.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_incomplete_afternoon_block`.

---

1. **Test case ID:** TC_004
2. **Test case title/description:** Unit-Test: Pausenregelung-Verstoss
3. **Preconditions:** `BreakTimeRule` und `TimeEntry` instanziert.
4. **Test steps:** Ein Arbeitstag über 5.5 Stunden am Stück (ohne Pause) wird durch die Rule (`check`) geprüft.
5. **Test data/input:** Arbeitszeit von 08:00 bis 14:00 Uhr (6 Stunden).
6. **Expected result:** Die Regel identifiziert fehlende Pause und meldet eine Violation zurück.
7. **Actual result:** Liste mit 1 Violation des Typs "Pausenregelung" wird generiert.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_break_time_rule_violation`.

---

1. **Test case ID:** TC_005
2. **Test case title/description:** Unit-Test: Maximalarbeitszeit-Verstoss
3. **Preconditions:** `MaxDailyWorkRule` und `TimeEntry` instanziert.
4. **Test steps:** Prüfe einen Eintrag, bei der über 14 Stunden gearbeitet wurde.
5. **Test data/input:** Morgen: 08:00-12:00 (4h), Nachmittag: 12:10-23:10 (11h), Total=15h.
6. **Expected result:** Violation aufgrund der Begrenzung wird ausgelöst.
7. **Actual result:** Exakt 1 Violation des Typs "Maximalarbeitszeit" wird gemeldet.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_max_daily_work_rule_violation`.

---

1. **Test case ID:** TC_006
2. **Test case title/description:** Unit-Test: Beschäftigungsgrad Grenzen validieren
3. **Preconditions:** Modell `Employee` involviert.
4. **Test steps:** Instanziierung eines Mitarbeiters mit ungültigen Werten beim Pensum.
5. **Test data/input:** Test 1: -10.0%, Test 2: 150.0%
6. **Expected result:** Das Domain-Modell weist beide ungültigen Pense via `ValueError` ab.
7. **Actual result:** `ValueError`s werden bei Instanziierungsversuch geworfen.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_employee_validates_employment_percentage`.

---

1. **Test case ID:** TC_007
2. **Test case title/description:** DB-Test: Employee speichern und laden
3. **Preconditions:** In-memory SQLite Datenbank über `conftest.py` Fixture.
4. **Test steps:** Nutze das `EmployeeRepository`, speichere ein neues `Employee` Profil und lese es mit der neu generierten ID neu ein.
5. **Test data/input:** `Employee(John Doe, john@test.ch, Pensum=80%)`
6. **Expected result:** Geladenes Profil ist identisch mit dem Eingabe-Profil.
7. **Actual result:** ID wurde aus DB vergeben und per Query korrekt rekonstruiert.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_employee_repository_saves_and_retrieves`.

---

1. **Test case ID:** TC_008
2. **Test case title/description:** DB-Test: TimeEntry Speichern mit Fremdschlüssel
3. **Preconditions:** Seeded Database enthält bereits mindestens einen Mitarbeiter.
4. **Test steps:** Speichere die Arbeitszeit über `TimeEntryRepository` mit Fremdschlüssel-ID 1 ab.
5. **Test data/input:** `TimeEntry(2026-04-20, 08:00-12:00, 13:00-17:00)` für Employee=1.
6. **Expected result:** Persistierungs-Vorgang erfolgreich, erneutes Laden durch Suchparameter (Datum) gibt exakt dieses `TimeEntry` aus.
7. **Actual result:** Objekt wurde an Mitarbeiter gelinkt gebunden gespeichert.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_time_entry_repository_saves_and_retrieves`.

---

1. **Test case ID:** TC_009
2. **Test case title/description:** DB-Test: TimeEntry nach Woche abfragen
3. **Preconditions:** Seeded Database, `TimeEntryRepository` bereit.
4. **Test steps:** Setze 3 unterschiedliche Einträge ab (zwei in der gleichen, einer in einer anderen Wochhe). Frage danach eine spezifische Woche via Repo-Methode ab.
5. **Test data/input:** Kalenderwochen-Speicherung: Woche 17 (2 Einträge), Woche 21 (1 Eintrag). Query: Woche 17.
6. **Expected result:** Exakt die abgefragte Teilliste (Länge 2) wird gemappt zurückgegeben.
7. **Actual result:** Query filtert erfolgreich (`len(week_entries) == 2`).
8. **Status:** Pass
9. **Comments:** Implementiert als `test_time_entry_repository_finds_entries_for_week`.

---

1. **Test case ID:** TC_010
2. **Test case title/description:** Integration-Test: Valid Day Entry ohne Verstösse
3. **Preconditions:** Orchestrierung über `TimeTrackingService` mit verbundener Repository-Mockstruktur.
4. **Test steps:** Via `add_work_day` einen korrekten Tag speichern und prüfen, ob die Repository-Komponente erfolgreich aufgerufen wird ohne Violations zu triggern.
5. **Test data/input:** 08:00 - 12:00 Uhr am Montag.
6. **Expected result:** Eintrag wird persistiert, keine Violations vom Service generiert.
7. **Actual result:** Eintrag `id is not None`, `len(violations) == 0`.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_integration_add_valid_work_day_saves_entry`.

---

1. **Test case ID:** TC_011
2. **Test case title/description:** Integration-Test: Valid Day Entry mit Überstunden-Trigger
3. **Preconditions:** Orchestrierung über `TimeTrackingService` mit verbundener Repository-Mockstruktur.
4. **Test steps:** Ein Arbeitsblock, der zu Pausenzeiten-Violations führt anlegen.
5. **Test data/input:** 08:00 - 14:30 Uhr durchgehender Arbeitsblock (6.5h).
6. **Expected result:** Der Service speichert den Eintrag in die DB und delegiert Violations durch die integrierten Checks an das Return-Object.
7. **Actual result:** Eintrag wird angelegt, aber Service reicht 1 Violation "Pausenregelung" durch.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_integration_add_work_day_with_overtime_triggers_violation`.

---

1. **Test case ID:** TC_012
2. **Test case title/description:** Integration-Test: Evaluate Week Summary Abfrage
3. **Preconditions:** Orchestrierung über `TimeTrackingService`.
4. **Test steps:** Speichern mehrerer Tage als Vorbereitung, anschließend Abfrage der summarischen Wochendaten via `get_employee_weekly_summary`.
5. **Test data/input:** Montag (4h) & Dienstag (2h) hinzugefügt. Wochen-Metrik wird abgeholt.
6. **Expected result:** Im Dictionary stehen korrekte Gesamtstunden inkl. der 2 registrierten Einzel-Zeilen.
7. **Actual result:** `total_hours == 6.0`, `len(entries) == 2` sowie kalkulierte negative Overtime für Teil-Woche.
8. **Status:** Pass
9. **Comments:** Implementiert als `test_integration_evaluate_week_summary`.

---

### Libraries Used

- see above

## 👥 Team & Contributions

---


| Name            | Contribution                      |
|-----------------|-----------------------------------|
| Arti Rechi      | NiceGUI UI + documentation        |
| Denis Meira     | Database & ORM + documentation    |
| Mehmedali Abdiu | Business logic + documentation    |

---

## 🤝 Contributing

---

> 🚧 This is a template repository for student projects.  
> 🚧 Do not change this section in your final submission.

- Use this repository as a starting point by importing it into your own GitHub account
- Work only within your own copy — do not push to the original template
- Commit regularly to track your progress

---

## 📝 License

---

This project is provided for **educational use only** as part of the Advanced Programming module.

[MIT License](LICENSE)

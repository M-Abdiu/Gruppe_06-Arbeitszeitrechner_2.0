"""
Zeiterfassungsanwendung – NiceGUI Hauptdatei.
Enthält alle UI-Seiten: Login, Worker-Dashboard, Admin-Dashboard.
Starte mit: python -m zeiterfassung  oder  python main.py
"""

from datetime import date, time, timedelta
from typing import Optional

from nicegui import ui, app
from sqlmodel import Session, select

from src.data_access.Database import engine, create_db_and_tables
from src.persistence.models import User, TimeEntry, Violation
from src.domain.users import Employee
from src.domain.time_tracking import TimeEntry as DomainTimeEntry
from src.domain.services import TimeTrackingService

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
WOCHENENDE = ["Samstag", "Sonntag"]

def decimal_to_hhmm(decimal_hours: float) -> str:
    if not decimal_hours:
        return ""
    hours = int(decimal_hours)
    minutes = int(round((decimal_hours - hours) * 60))
    return f"{hours:02d}:{minutes:02d}"

def hhmm_to_decimal(time_str: str) -> float:
    if not time_str or time_str.strip() == "":
        return 0.0
        
    parts = time_str.split(':')
    if len(parts) != 2:
        raise ValueError(f"Ungültiges Format '{time_str}', erwartet HH:MM")
        
    try:
        h = int(parts[0])
        m = int(parts[1])
    except ValueError:
        raise ValueError(f"Ungültiges Format '{time_str}', erwartet HH:MM")
        
    if h > 23 or m > 59 or h < 0 or m < 0:
        raise ValueError(f"Ungültige Zeit '{time_str}'")
        
    return h + m / 60.0

def decimal_to_time(decimal_hours: float) -> time:
    if not decimal_hours:
        return None
    hours = int(decimal_hours)
    minutes = int(round((decimal_hours - hours) * 60))
    if hours >= 24:
        hours = 23
        minutes = 59
    return time(hours, minutes)

def get_weekly_summary(db_user: User, db_entries: list[TimeEntry]) -> dict:
    """Brücke zwischen UI, Datenbank und der echten Domain Logik."""
    try:
        # Falls keine Einträge vorhanden, aber wir dennoch aufgerufen werden
        if not db_entries:
            e = Employee(db_user.Vorname, db_user.Nachname, "test@test.com", db_user.Pensum, entity_id=str(db_user.pk_user_id))
            return {
                "effektiv": 0.0,
                "soll": e.get_weekly_target_hours(),
                "differenz": -e.get_weekly_target_hours(),
                "pausen": 0.0,
                "verletzt": False,
                "verletzungen": []
            }
            
        kw = db_entries[0].Kalenderwoche
        jahr = db_entries[0].Jahr
        
        # 1. Konvertiere User in Domain Model
        emp = Employee(
            first_name=db_user.Vorname, 
            last_name=db_user.Nachname, 
            email="mock@example.com", 
            employment_percentage=db_user.Pensum,
            entity_id=str(db_user.pk_user_id)
        )
        
        service = TimeTrackingService()
        
        all_violations = []
        domain_entries = []
        total_pausen = 0.0
        total_effektiv = 0.0
        
        # Wochentage in isocalendar Tag-Index (1=Montag..7=Sonntag) umwandeln
        wd_map = {wd: i+1 for i, wd in enumerate(WOCHENTAGE + WOCHENENDE)}
        
        for db_e in db_entries:
            # Falls der Eintrag komplett leer ist
            if not any([db_e.MorgenBeginn, db_e.MorgenStop, db_e.NachmittagBeginn, db_e.NachmittagStop]):
                continue
                
            day_idx = wd_map.get(db_e.Tag, 1)
            # Baue korrektes Datum für dieses Jahr/KW/Tag
            entry_date = date.fromisocalendar(jahr, kw, day_idx)
            
            ds_start = decimal_to_time(db_e.MorgenBeginn) or time(0,0)
            ds_end = decimal_to_time(db_e.MorgenStop) or time(0,0)
            da_start = decimal_to_time(db_e.NachmittagBeginn)
            da_end = decimal_to_time(db_e.NachmittagStop)
            
            try:
                dom_e, day_violations = service.add_work_day(
                    employee=emp, entry_date=entry_date,
                    morning_start=ds_start, morning_end=ds_end,
                    afternoon_start=da_start, afternoon_end=da_end
                )
                domain_entries.append(dom_e)
                all_violations.extend(day_violations)
                
                pausen_delta = dom_e.calculate_break_time()
                total_pausen += pausen_delta.total_seconds() / 3600.0
                
                work_delta = dom_e.calculate_work_hours()
                total_effektiv += work_delta.total_seconds() / 3600.0
                
            except ValueError as val_err:
                # Chronologie-Fehler beim Aufbau des Domain Objekts
                from src.domain.violations import Violation as DomViol
                all_violations.append(DomViol("Fehlerhafte Einträge", str(val_err), entry_date))

        # 3. Wochenauswertung aufrufen
        try:
            week_obj, week_violations = service.evaluate_week(emp, jahr, kw, domain_entries)
            all_violations.extend(week_violations)
            
            soll_td = week_obj.calculate_target_hours()
            diff_td = week_obj.calculate_overtime()
            
            soll = soll_td.total_seconds() / 3600.0
            differenz = diff_td.total_seconds() / 3600.0
        except ValueError as val_err:
             from src.domain.violations import Violation as DomViol
             all_violations.append(DomViol("Ungültige Woche", str(val_err), None))
             soll = emp.get_weekly_target_hours()
             differenz = total_effektiv - soll

        return {
            "effektiv": total_effektiv,
            "soll": soll,
            "differenz": differenz,
            "pausen": total_pausen,
            "verletzt": len(all_violations) > 0,
            "verletzungen": all_violations
        }
    except Exception as e:
        import traceback
        print("FEHLER", traceback.format_exc())
        return {
            "effektiv": 0.0, "soll": 0.0, "differenz": 0.0, "pausen": 0.0,
            "verletzt": True, "verletzungen": []
        }

def get_session():
    return Session(engine)



# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def get_current_user() -> Optional[User]:
    """Gibt den aktuell eingeloggten User zurück oder None."""
    user_id = app.storage.user.get("user_id")
    if not user_id:
        return None
    with get_session() as session:
        return session.get(User, user_id)


def require_login(is_admin_required: bool = False):
    """Weiterleitung zur Login-Seite falls nicht eingeloggt."""
    user_id = app.storage.user.get("user_id")
    if not user_id:
        ui.navigate.to("/")
        return False
    if is_admin_required and not app.storage.user.get("is_admin"):
        ui.navigate.to("/worker")
        return False
    return True


def logout():
    app.storage.user.clear()
    ui.navigate.to("/")


def format_diff(diff: float) -> str:
    sign = "+" if diff > 0 else ""
    return f"{sign}{diff:.2f} h"


def get_current_kw() -> tuple[int, int]:
    """Gibt aktuelle Kalenderwoche und Jahr zurück."""
    today = date.today()
    return today.isocalendar().week, today.year


# ── Gemeinsame UI-Komponenten ────────────────────────────────────────────────

def header_bar(title: str):
    """Gemeinsame Navigationsleiste."""
    with ui.header().classes("bg-blue-700 text-white px-6 py-3 flex items-center justify-between"):
        ui.label(f"⏱ Zeiterfassung | {title}").classes("text-lg font-semibold")
        with ui.row().classes("items-center gap-4"):
            name = app.storage.user.get("vorname", "")
            role = "Admin" if app.storage.user.get("is_admin") else "Worker"
            ui.label(f"{name} ({role})").classes("text-sm opacity-80")
            ui.button("Abmelden", on_click=logout).props("flat color=white dense")


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN-SEITE
# ══════════════════════════════════════════════════════════════════════════════

@ui.page("/")
def login_page():
    ui.query("body").style("background: #EFF6FF")

    with ui.column().classes("items-center justify-center w-full min-h-screen"):
        with ui.card().classes("w-96 shadow-xl rounded-2xl p-8"):
            ui.label("⏱ Zeiterfassung").classes(
                "text-3xl font-bold text-blue-700 text-center w-full"
            )
            ui.label("Bitte anmelden").classes(
                "text-gray-400 text-center w-full mb-6"
            )

            username_input = ui.input(
                "Benutzername", placeholder="z.B. admin01"
            ).classes("w-full")
            password_input = (
                ui.input("Passwort", password=True, password_toggle_button=True)
                .classes("w-full mt-3")
            )
            error_label = ui.label("").classes("text-red-500 text-sm mt-1")

            def do_login():
                with Session(engine) as session:
                    user = session.exec(
                        select(User).where(User.username == username_input.value)
                    ).first()

                    if user and user.Passwort == password_input.value:
                        app.storage.user["user_id"] = user.pk_user_id
                        app.storage.user["username"] = user.username
                        app.storage.user["is_admin"] = user.IsAAdmin
                        app.storage.user["vorname"] = user.Vorname
                        app.storage.user["nachname"] = user.Nachname
                        if user.IsAAdmin:
                            ui.navigate.to("/admin")
                        else:
                            ui.navigate.to("/worker")
                    else:
                        error_label.text = "❌ Ungültiger Benutzername oder Passwort"

            password_input.on("keydown.enter", do_login)

            ui.button("Anmelden", on_click=do_login).classes(
                "w-full mt-5 bg-blue-700 text-white rounded-lg"
            ).props("size=lg")

        ui.label("Demo: admin01/1234  |  berisha/1234").classes(
            "text-gray-400 text-xs mt-4"
        )


# ══════════════════════════════════════════════════════════════════════════════
# WORKER-SEITE
# ══════════════════════════════════════════════════════════════════════════════

@ui.page("/worker")
def worker_page():
    if not require_login():
        return

    header_bar("Mein Bereich")

    user_id = app.storage.user.get("user_id")
    current_kw, current_year = get_current_kw()

    # ── State ──────────────────────────────────────────────────────────────
    selected_kw = {"kw": current_kw, "year": current_year}

    # ── Zeit-Eingabe-Felder (Montag–Freitag + Wochenende) ─────────────────
    time_fields: dict[str, dict[str, ui.input]] = {}

    def load_entries_to_form():
        """Lädt vorhandene Einträge in die Formularfelder."""
        with Session(engine) as session:
            for tag in WOCHENTAGE + WOCHENENDE:
                entry = session.exec(
                    select(TimeEntry).where(
                        TimeEntry.fk_user_id == user_id,
                        TimeEntry.Kalenderwoche == selected_kw["kw"],
                        TimeEntry.Jahr == selected_kw["year"],
                        TimeEntry.Tag == tag,
                    )
                ).first()

                if entry and tag in time_fields:
                    tf = time_fields[tag]
                    tf["mb"].value = decimal_to_hhmm(entry.MorgenBeginn)
                    tf["ms"].value = decimal_to_hhmm(entry.MorgenStop)
                    tf["nb"].value = decimal_to_hhmm(entry.NachmittagBeginn)
                    tf["ns"].value = decimal_to_hhmm(entry.NachmittagStop)
                elif tag in time_fields:
                    tf = time_fields[tag]
                    for f in tf.values():
                        f.value = ""

    def save_entries():
        """Speichert alle Formularfelder als Zeiteinträge in der DB."""
        # Validation via Domain Logic (DomainTimeEntry constructor validates times)
        invalid_days = []
        for tag in WOCHENTAGE + WOCHENENDE:
            if tag not in time_fields:
                continue
            tf = time_fields[tag]
            try:
                mb = hhmm_to_decimal(tf["mb"].value)
                ms = hhmm_to_decimal(tf["ms"].value)
                nb = hhmm_to_decimal(tf["nb"].value)
                ns = hhmm_to_decimal(tf["ns"].value)

                if mb == 0.0 and ms == 0.0 and nb == 0.0 and ns == 0.0:
                    continue

                # Check validity using domain rules
                # We use date.today() as a placeholder just to trigger the internal _validate_times
                DomainTimeEntry(
                    entry_date=date.today(),
                    morning_start=decimal_to_time(mb) or time(0, 0),
                    morning_end=decimal_to_time(ms) or time(0, 0),
                    afternoon_start=decimal_to_time(nb),
                    afternoon_end=decimal_to_time(ns)
                )
            except ValueError as e:
                invalid_days.append(f"{tag} ({str(e)})")

        if invalid_days:
            ui.notify(f"❌ Ungültige Zeiteingabe: {', '.join(invalid_days)}", type="negative")
            return

        with Session(engine) as session:
            saved_count = 0
            for tag in WOCHENTAGE + WOCHENENDE:
                if tag not in time_fields:
                    continue
                tf = time_fields[tag]
                mb = hhmm_to_decimal(tf["mb"].value)
                ms = hhmm_to_decimal(tf["ms"].value)
                nb = hhmm_to_decimal(tf["nb"].value)
                ns = hhmm_to_decimal(tf["ns"].value)

                # Nur speichern wenn etwas eingetragen wurde
                if mb == 0.0 and ms == 0.0 and nb == 0.0 and ns == 0.0:
                    # Bestehenden leeren Eintrag löschen (falls vorhanden)
                    existing = session.exec(
                        select(TimeEntry).where(
                            TimeEntry.fk_user_id == user_id,
                            TimeEntry.Kalenderwoche == selected_kw["kw"],
                            TimeEntry.Jahr == selected_kw["year"],
                            TimeEntry.Tag == tag,
                        )
                    ).first()
                    if existing:
                        session.delete(existing)
                    continue

                existing = session.exec(
                    select(TimeEntry).where(
                        TimeEntry.fk_user_id == user_id,
                        TimeEntry.Kalenderwoche == selected_kw["kw"],
                        TimeEntry.Jahr == selected_kw["year"],
                        TimeEntry.Tag == tag,
                    )
                ).first()

                if existing:
                    existing.MorgenBeginn = mb
                    existing.MorgenStop = ms
                    existing.NachmittagBeginn = nb
                    existing.NachmittagStop = ns
                    session.add(existing)
                else:
                    new_entry = TimeEntry(
                        fk_user_id=user_id,
                        Kalenderwoche=selected_kw["kw"],
                        Jahr=selected_kw["year"],
                        Tag=tag,
                        MorgenBeginn=mb,
                        MorgenStop=ms,
                        NachmittagBeginn=nb,
                        NachmittagStop=ns,
                    )
                    session.add(new_entry)
                saved_count += 1

            session.commit()

        ui.notify(f"✅ {saved_count} Einträge für KW {selected_kw['kw']}/{selected_kw['year']} gespeichert.", type="positive")
        load_entries_to_form()
        refresh_overview.refresh()

    # ── Tabs ───────────────────────────────────────────────────────────────
    with ui.tabs().classes("w-full") as tabs:
        tab_erfassen = ui.tab("Stunden erfassen", icon="edit")
        tab_uebersicht = ui.tab("Meine Übersicht", icon="bar_chart")

    with ui.tab_panels(tabs, value=tab_erfassen).classes("w-full p-4"):

        # ── TAB 1: Stunden erfassen ────────────────────────────────────────
        with ui.tab_panel(tab_erfassen):
            with ui.card().classes("w-full max-w-3xl mx-auto shadow-md rounded-xl p-6"):
                ui.label("📅 Kalenderwoche auswählen").classes("text-lg font-semibold text-gray-700 mb-4")

                with ui.row().classes("items-end gap-4 mb-6"):
                    kw_input = (
                        ui.number("KW", value=current_kw, min=1, max=53)
                        .classes("w-24")
                    )
                    year_input = (
                        ui.number("Jahr", value=current_year, min=2020, max=2099)
                        .classes("w-28")
                    )

                    def on_kw_change():
                        selected_kw["kw"] = int(kw_input.value or current_kw)
                        selected_kw["year"] = int(year_input.value or current_year)
                        load_entries_to_form()

                    ui.button("Laden", on_click=on_kw_change).props("flat color=primary")

                # ── Tabellenkopf ──────────────────────────────────────────
                with ui.grid(columns=5).classes("w-full gap-2 font-semibold text-gray-500 text-sm px-2"):
                    ui.label("Tag")
                    ui.label("Morgen Beginn")
                    ui.label("Morgen Stop")
                    ui.label("Nachmittag Beginn")
                    ui.label("Nachmittag Stop")

                ui.separator()

                # ── Zeitfelder pro Tag ───────────────────────────────────
                all_days = WOCHENTAGE + WOCHENENDE
                for tag in all_days:
                    is_weekend = tag in WOCHENENDE
                    row_color = "bg-orange-50" if is_weekend else "bg-white"

                    with ui.grid(columns=5).classes(
                        f"w-full gap-2 items-center px-2 py-1 rounded {row_color}"
                    ):
                        label_color = "text-orange-600 font-semibold" if is_weekend else "text-gray-700 font-medium"
                        ui.label(tag).classes(label_color)

                        placeholder = "HH:MM"
                        mb = ui.input(placeholder=placeholder).props("dense outlined").classes("w-full")
                        ms = ui.input(placeholder=placeholder).props("dense outlined").classes("w-full")
                        nb = ui.input(placeholder=placeholder).props("dense outlined").classes("w-full")
                        ns = ui.input(placeholder=placeholder).props("dense outlined").classes("w-full")

                        time_fields[tag] = {"mb": mb, "ms": ms, "nb": nb, "ns": ns}

                ui.separator().classes("my-4")

                with ui.row().classes("gap-4"):
                    ui.button("💾 Speichern", on_click=save_entries).classes(
                        "bg-blue-700 text-white"
                    ).props("size=md")
                    ui.button("🔄 Zurücksetzen", on_click=lambda: [
                        setattr(f, "value", "") for tf in time_fields.values() for f in tf.values()
                    ]).props("flat color=grey size=md")

                ui.label("Format: HH:MM (z.B. 08:30)  |  Leer lassen = kein Eintrag").classes(
                    "text-xs text-gray-400 mt-2"
                )

        # ── TAB 2: Eigene Übersicht ────────────────────────────────────────
        with ui.tab_panel(tab_uebersicht):

            @ui.refreshable
            def refresh_overview():
                with Session(engine) as session:
                    user = session.get(User, user_id)
                    if not user:
                        return

                    # Alle Einträge dieses Users gruppiert nach KW/Jahr
                    all_entries = session.exec(
                        select(TimeEntry)
                        .where(TimeEntry.fk_user_id == user_id)
                        .order_by(TimeEntry.Jahr.desc(), TimeEntry.Kalenderwoche.desc())
                    ).all()

                    # Gruppieren nach (kw, jahr)
                    weeks: dict[tuple, list] = {}
                    for e in all_entries:
                        key = (e.Kalenderwoche, e.Jahr)
                        weeks.setdefault(key, []).append(e)

                if not weeks:
                    ui.label("Noch keine Zeiteinträge vorhanden.").classes("text-gray-400 mt-8")
                    return

                ui.label("📊 Meine Wochenübersicht").classes("text-lg font-semibold text-gray-700 mb-4")

                # Übersichtstabelle
                columns = [
                    {"name": "kw", "label": "KW", "field": "kw", "sortable": True},
                    {"name": "jahr", "label": "Jahr", "field": "jahr"},
                    {"name": "effektiv", "label": "Ist-Zeit", "field": "effektiv"},
                    {"name": "soll", "label": "Soll-Zeit", "field": "soll"},
                    {"name": "differenz", "label": "Differenz", "field": "differenz"},
                    {"name": "pausen", "label": "Pausen", "field": "pausen"},
                    {"name": "status", "label": "Status", "field": "status"},
                ]

                rows = []
                for (kw, jahr), entries in sorted(weeks.items(), reverse=True):
                    with Session(engine) as session:
                        u = session.get(User, user_id)
                        summ = get_weekly_summary(u, entries)
                    rows.append({
                        "kw": kw,
                        "jahr": jahr,
                        "effektiv": f"{summ['effektiv']:.2f} h",
                        "soll": f"{summ['soll']:.2f} h",
                        "differenz": format_diff(summ["differenz"]),
                        "pausen": f"{summ['pausen']:.2f} h",
                        "status": "❌ Verletzt" if summ["verletzt"] else "✅ OK",
                    })

                table = ui.table(columns=columns, rows=rows, row_key="kw").classes("w-full")
                table.add_slot("body-cell-status", """
                    <q-td :props="props">
                        <span :class="props.value.includes('❌') ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold'">
                            {{ props.value }}
                        </span>
                    </q-td>
                """)
                table.add_slot("body-cell-differenz", """
                    <q-td :props="props">
                        <span :class="props.value.startsWith('+') ? 'text-green-600' : props.value.startsWith('-') ? 'text-red-600' : ''">
                            {{ props.value }}
                        </span>
                    </q-td>
                """)

                # Detailansicht: Verstösse
                for (kw, jahr), entries in sorted(weeks.items(), reverse=True):
                    with Session(engine) as session:
                        u = session.get(User, user_id)
                        summ = get_weekly_summary(u, entries)

                    if summ["verletzt"]:
                        with ui.expansion(
                            f"⚠️  Verstösse KW {kw}/{jahr}", icon="warning"
                        ).classes("w-full mt-2 border border-orange-300 rounded-lg"):
                            for v in summ["verletzungen"]:
                                with ui.row().classes("items-center gap-2 p-2"):
                                    ui.badge(v.type, color="orange")
                                    ui.label(v.message).classes("text-sm text-gray-600")

            refresh_overview()

    # Beim Laden der Seite Felder befüllen
    load_entries_to_form()


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN-SEITE
# ══════════════════════════════════════════════════════════════════════════════

@ui.page("/admin")
def admin_page():
    if not require_login(is_admin_required=True):
        return

    header_bar("Admin-Bereich")

    current_kw, current_year = get_current_kw()
    selected = {"kw": current_kw, "year": current_year}

    with ui.tabs().classes("w-full") as tabs:
        tab_uebersicht = ui.tab("Übersicht", icon="table_chart")
        tab_verstoesse = ui.tab("Verstösse", icon="warning")
        tab_users = ui.tab("Benutzerverwaltung", icon="people")

    with ui.tab_panels(tabs, value=tab_uebersicht).classes("w-full p-4"):

        # ── TAB 1: Übersicht ───────────────────────────────────────────────
        with ui.tab_panel(tab_uebersicht):

            with ui.row().classes("items-end gap-4 mb-4"):
                ui.label("Übersicht Kalenderwoche:").classes("font-semibold text-gray-700")
                kw_sel = ui.number("KW", value=current_kw, min=1, max=53).classes("w-24")
                year_sel = ui.number("Jahr", value=current_year, min=2020, max=2099).classes("w-28")

                def reload_uebersicht():
                    selected["kw"] = int(kw_sel.value or current_kw)
                    selected["year"] = int(year_sel.value or current_year)
                    refresh_uebersicht.refresh()

                ui.button("Anzeigen", on_click=reload_uebersicht).props("color=primary")

            @ui.refreshable
            def refresh_uebersicht():
                kw = selected["kw"]
                jahr = selected["year"]

                ui.label(f"📋 KW {kw} / {jahr}").classes("text-lg font-semibold text-gray-600 mb-3")

                columns = [
                    {"name": "nachname", "label": "Nachname", "field": "nachname", "sortable": True},
                    {"name": "vorname", "label": "Vorname", "field": "vorname"},
                    {"name": "pensum", "label": "Pensum %", "field": "pensum"},
                    {"name": "effektiv", "label": "Ist-Zeit", "field": "effektiv"},
                    {"name": "soll", "label": "Soll-Zeit", "field": "soll"},
                    {"name": "differenz", "label": "Differenz", "field": "differenz"},
                    {"name": "pausen", "label": "Pausen", "field": "pausen"},
                    {"name": "status", "label": "Vertragsbedingung", "field": "status"},
                    {"name": "begruendung", "label": "Begründung", "field": "begruendung"},
                ]

                rows = []
                with Session(engine) as session:
                    workers = session.exec(
                        select(User).where(User.IsAAdmin == False)
                    ).all()

                    for worker in workers:
                        entries = session.exec(
                            select(TimeEntry).where(
                                TimeEntry.fk_user_id == worker.pk_user_id,
                                TimeEntry.Kalenderwoche == kw,
                                TimeEntry.Jahr == jahr,
                            )
                        ).all()

                        summ = get_weekly_summary(worker, list(entries))
                        begruendung = (
                            ", ".join(v.type for v in summ["verletzungen"])
                            if summ["verletzt"] else "–"
                        )

                        rows.append({
                            "nachname": worker.Nachname,
                            "vorname": worker.Vorname,
                            "pensum": f"{worker.Pensum} %",
                            "effektiv": f"{summ['effektiv']:.2f} h",
                            "soll": f"{summ['soll']:.2f} h",
                            "differenz": format_diff(summ["differenz"]),
                            "pausen": f"{summ['pausen']:.2f} h",
                            "status": "❌ Verletzt" if summ["verletzt"] else "✅ Eingehalten",
                            "begruendung": begruendung,
                        })

                table = ui.table(columns=columns, rows=rows, row_key="nachname").classes("w-full")
                table.add_slot("body-cell-status", """
                    <q-td :props="props">
                        <span :class="props.value.includes('❌') ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold'">
                            {{ props.value }}
                        </span>
                    </q-td>
                """)
                table.add_slot("body-cell-differenz", """
                    <q-td :props="props">
                        <span :class="props.value.startsWith('+') ? 'text-green-600' : props.value.startsWith('-') ? 'text-red-600' : ''">
                            {{ props.value }}
                        </span>
                    </q-td>
                """)

            refresh_uebersicht()

        # ── TAB 2: Verstösse ───────────────────────────────────────────────
        with ui.tab_panel(tab_verstoesse):

            with ui.row().classes("items-end gap-4 mb-4"):
                ui.label("Verstösse für KW:").classes("font-semibold text-gray-700")
                kw_v = ui.number("KW", value=current_kw, min=1, max=53).classes("w-24")
                year_v = ui.number("Jahr", value=current_year, min=2020, max=2099).classes("w-28")
                sel_v = {"kw": current_kw, "year": current_year}

                def reload_verstoesse():
                    sel_v["kw"] = int(kw_v.value or current_kw)
                    sel_v["year"] = int(year_v.value or current_year)
                    refresh_verstoesse.refresh()

                ui.button("Anzeigen", on_click=reload_verstoesse).props("color=primary")

            @ui.refreshable
            def refresh_verstoesse():
                kw = sel_v["kw"]
                jahr = sel_v["year"]

                with Session(engine) as session:
                    workers = session.exec(
                        select(User).where(User.IsAAdmin == False)
                    ).all()

                has_violations = False
                for worker in workers:
                    with Session(engine) as session:
                        entries = session.exec(
                            select(TimeEntry).where(
                                TimeEntry.fk_user_id == worker.pk_user_id,
                                TimeEntry.Kalenderwoche == kw,
                                TimeEntry.Jahr == jahr,
                            )
                        ).all()
                        summ = get_weekly_summary(worker, list(entries))

                    if not summ["verletzt"]:
                        continue

                    has_violations = True
                    with ui.card().classes("w-full mb-4 border-l-4 border-red-500 shadow"):
                        with ui.row().classes("items-center justify-between p-4"):
                            ui.label(
                                f"👤 {worker.Nachname}, {worker.Vorname}  |  {worker.Pensum}%  |  KW {kw}"
                            ).classes("font-semibold text-gray-700")
                            ui.badge(f"{len(summ['verletzungen'])} Verstoss/Verstösse", color="red")

                        with ui.column().classes("px-4 pb-4 gap-2"):
                            for v in summ["verletzungen"]:
                                with ui.row().classes("items-start gap-3 bg-red-50 rounded p-2"):
                                    ui.icon("warning", color="orange").classes("mt-0.5")
                                    with ui.column().classes("gap-0"):
                                        ui.label(v.type).classes("font-semibold text-sm text-orange-700")
                                        ui.label(v.message).classes("text-sm text-gray-600")

                if not has_violations:
                    with ui.column().classes("items-center mt-12"):
                        ui.icon("check_circle", color="green", size="4em")
                        ui.label(f"Keine Verstösse in KW {kw}/{jahr} 🎉").classes(
                            "text-green-600 font-semibold text-lg mt-2"
                        )

            refresh_verstoesse()

        # ── TAB 3: Benutzerverwaltung ──────────────────────────────────────
        with ui.tab_panel(tab_users):

            @ui.refreshable
            def refresh_users():
                ui.label("👥 Mitarbeitende").classes("text-lg font-semibold text-gray-700 mb-4")

                with Session(engine) as session:
                    users = session.exec(select(User)).all()

                columns = [
                    {"name": "id", "label": "ID", "field": "id"},
                    {"name": "username", "label": "Benutzername", "field": "username"},
                    {"name": "vorname", "label": "Vorname", "field": "vorname"},
                    {"name": "nachname", "label": "Nachname", "field": "nachname"},
                    {"name": "email", "label": "E-Mail", "field": "email"},
                    {"name": "pensum", "label": "Pensum %", "field": "pensum"},
                    {"name": "rolle", "label": "Rolle", "field": "rolle"},
                    {"name": "aktion", "label": "Aktion", "field": "aktion"},
                ]

                rows = [
                    {
                        "id": u.pk_user_id,
                        "username": u.username,
                        "vorname": u.Vorname,
                        "nachname": u.Nachname,
                        "email": u.Email,
                        "pensum": f"{u.Pensum} %",
                        "rolle": "Admin" if u.IsAAdmin else "Worker",
                        "aktion": str(u.pk_user_id),
                    }
                    for u in users
                ]

                table = ui.table(columns=columns, rows=rows, row_key="id").classes("w-full mb-6")
                table.add_slot("body-cell-aktion", """
                    <q-td :props="props">
                        <q-btn flat dense color="red" icon="delete"
                            @click="$parent.$emit('delete', props.row)" />
                    </q-td>
                """)

                def handle_delete(e):
                    uid = e.args["id"]
                    admin_id = app.storage.user.get("user_id")
                    if uid == admin_id:
                        ui.notify("❌ Du kannst dich nicht selbst löschen.", type="negative")
                        return
                    with Session(engine) as session:
                        u = session.get(User, uid)
                        if u:
                            # Zeiteinträge iterativ über SQL löschen, da keine Relationship existiert
                            entries = session.exec(select(TimeEntry).where(TimeEntry.fk_user_id == uid)).all()
                            for ze in entries:
                                violations = session.exec(select(Violation).where(Violation.fk_TimeEntry_id == ze.pk_TimeEntry_id)).all()
                                for viol in violations:
                                    session.delete(viol)
                                session.delete(ze)
                            session.delete(u)
                            session.commit()
                    ui.notify(f"✅ Benutzer gelöscht.", type="positive")
                    refresh_users.refresh()

                table.on("delete", handle_delete)

            refresh_users()

            # ── Neuen Benutzer anlegen ──────────────────────────────────
            with ui.card().classes("w-full max-w-xl shadow rounded-xl p-6"):
                ui.label("➕ Neuen Mitarbeitenden erfassen").classes("text-md font-semibold text-gray-700 mb-4")

                with ui.grid(columns=2).classes("w-full gap-3"):
                    n_username = ui.input("Benutzername *").props("outlined dense")
                    n_passwort = ui.input("Passwort *", password=True).props("outlined dense")
                    n_vorname = ui.input("Vorname *").props("outlined dense")
                    n_nachname = ui.input("Nachname *").props("outlined dense")
                    n_email = ui.input("E-Mail").props("outlined dense")
                    n_pensum = ui.number("Pensum %", value=100, min=10, max=100).props("outlined dense")

                def toggle_pensum(e):
                    if e.value:
                        n_pensum.disable()
                    else:
                        n_pensum.enable()

                n_is_admin = ui.checkbox("Admin-Rolle", on_change=toggle_pensum).classes("mt-2")

                def create_user():
                    if not n_username.value or not n_passwort.value or not n_vorname.value or not n_nachname.value:
                        ui.notify("❌ Pflichtfelder ausfüllen (mit * markiert).", type="negative")
                        return

                    with Session(engine) as session:
                        existing = session.exec(
                            select(User).where(User.username == n_username.value)
                        ).first()
                        if existing:
                            ui.notify(f"❌ Benutzername '{n_username.value}' bereits vergeben.", type="negative")
                            return

                        new_user = User(
                            username=n_username.value.strip(),
                            Vorname=n_vorname.value.strip(),
                            Nachname=n_nachname.value.strip(),
                            Email=n_email.value.strip(),
                            Passwort=n_passwort.value,
                            IsAAdmin=n_is_admin.value,
                            Pensum=0 if n_is_admin.value else int(n_pensum.value or 100),
                        )
                        session.add(new_user)
                        session.commit()

                    ui.notify(f"✅ Benutzer '{n_username.value}' erstellt.", type="positive")
                    for f in [n_username, n_passwort, n_vorname, n_nachname, n_email]:
                        f.value = ""
                    n_pensum.value = 100
                    n_is_admin.value = False
                    refresh_users.refresh()

                ui.button("Benutzer anlegen", on_click=create_user).classes(
                    "bg-blue-700 text-white mt-4"
                ).props("size=md")


# ══════════════════════════════════════════════════════════════════════════════
# APP-START
# ══════════════════════════════════════════════════════════════════════════════

def seed_data():
    with get_session() as session:
        if session.exec(select(User)).first() is None:
            admin = User(
                username="admin01",
                Passwort="1234",
                Vorname="Admin",
                Nachname="User",
                Email="admin@example.com",
                IsAAdmin=True,
                Pensum=100
            )
            worker = User(
                username="berisha",
                Passwort="1234",
                Vorname="Arben",
                Nachname="Berisha",
                Email="berisha@example.com",
                IsAAdmin=False,
                Pensum=80
            )
            session.add(admin)
            session.add(worker)
            session.commit()

def main():
    create_db_and_tables()
    seed_data()

    ui.run(
        title="Zeiterfassung",
        port=8080,
        storage_secret="zeiterfassung-geheim-2025",
        favicon="⏱",
        dark=False,
    )


if __name__ == "__main__":
    main()

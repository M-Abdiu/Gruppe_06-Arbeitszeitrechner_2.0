# Arbeitszeit-Auswertungs Programm

> 🚧 Replace the screenshot with one that shows your main screen.

![UI Showcase](docs/ui-images/ui_showcase.png)

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

Der User will eine Übersicht über die Stunden haben, indem ein er ein File importiert, welches die wöchentliche Stemplungen der Mitarbeiter beinhaltet. Schlussendlich soll er als Output im Browser , eine Übersicht erhalten in der aufgeführt ist:
- Nachname, Vorname, Pensum
- Effektivstunden
- Soll-Zeit
- Differenz-Zeit
- Pausen-Zeit
- Vertragsbedingungen eingehalten?
- Begründung der Vertrags-Verletzung

Der User soll ene Gesamtübersicht erhalten, aber auch die Option haben, individuelle Mitarbeterauszüge nach Kalenderwoche anzuschauen.
---

## User Stories

### 1. Worker: Login
**Als User möchte ich, mich einloggen und meine Module sehen basierend auf meiner Berechtigung**
**Description:**
**Inputs:** none  
**Outputs:**

### 2. Worker: Hour Logging
**Als User möchte ich, mich einloggen und meine Arbeitsstunden eintragen für eine Kalenderwoche**
**Description:**
**Inputs:** none  
**Outputs:**

### 3. Worker: Hour Overview
**Als User möchte ich, mich einloggen und meine individuelle Arbeitsstundenauszüge sehen**
**Description:**
**Inputs:** none  
**Outputs:**

### 1. Admin: Login
**Als Admin möchte ich, mich einloggen und meine Module sehen basierend auf meiner Berechtigung**
**Description:**
**Inputs:** none  
**Outputs:**

### 2. Admin:View Admin Worktime Menu
**Als Admin möchte ich, eine Übersicht der Soll-Zeit, Differenz-Zeit,Pensums jedes einzelnen Mitarbeiters erhalten.**
**Description:**
**Inputs:** none  
**Outputs:**

### 3. Admin: View Violations Menu
**Als Admin möchte ich, eine Angabe erhalten ob die vertraglichen Rahmenbedingungen eingehalten wurden und gegebenenfalls eine Angabe erhalten welche Rahmenbedingung verletzt wurde pro Mitarbeiter.**
**Description:**
**Inputs:** none  
**Outputs:**

### 4. Admin: User Managment Menu 
**Als Admin möchte ich,neue Mitarbeiter erfassen oder entfernen.**
**Description:**
**Inputs:** none  
**Outputs:**

---

### Use cases

> 🚧 Name actors and briefly describe each use case. Ideally, a UML use case diagram specifies use cases and relationships.

![UML Use Case Diagram](docs/architecture-diagrams/uml_use_case_diagram.png)

**Use cases**
## Main Use Cases

- Startseite (Worker, Admin)  
- individueller Stundenauszug (Worker)  
  - neuer Wocheneintrag (Worker) 
- Stundenauszugübersicht (Admin)  
- Verletzungsübersicht (Admin)    
- User Management (Admin)  

**Actors**
- Worker (Zeiterfassung,individueller Stundenauszug)
- Admin (Stundenauszug pro Mitarbeiter überprüfen, Arbeitsvertragsverletzungsüberscht überprüfen, Neue Mitarbeiter erfassen oder entfernen )

---

### Wireframes / Mockups

> 🚧 Add screenshots of the wireframe mockups you chose to implement.

![Wireframes – Home/Transactions](docs/ui-images/wireframes.png)

---

## 🏛️ Architecture

> 🚧 Document the architecture components, relationships, and key design decisions.

### Software Architecture

> 🚧 Insert your UML class diagram(s). Split into multiple diagrams if needed.

![UML Class Diagram](docs/architecture-diagrams/uml_class_architecture.png)

**Layers / components:**
- UI (NiceGUI pages/components, browser as thin client)
- Application logic (controllers + domain/services)
- Persistence (SQLite + ORM entities + repositories/queries)

**Design decisions (examples):**
- Organize code using **MVC**:
   - **Model:** domain + ORM entities (e.g. `models.py`)
   - **View:** NiceGUI UI components/pages
   - **Controller:** event handlers and coordination logic between UI, services, and persistence
- Separate UI (`app/main.py`) from domain logic (e.g. `pricing.py`) and persistence (e.g. `models.py`, `db.py`)
- Use and interaction of modules to minimize dependencies, by minimizing cohesion and maximizing coupling
- Keep business rules testable without starting the UI

**Design patterns used (examples):**
- MVC (Model–View–Controller)
- Repository/DAO for database access (e.g. `queries.py`)
- Strategy for business rules (e.g. discount calculation)
- Adapter for external services (e.g. invoice generation backend)

---

### 🗄️ Database and ORM

> 🚧 Describe the database and your ORM entities. Ideally, a diagram documents the database and it is described together with the ORM entities.

![ER Diagram](docs/architecture-diagrams/er_diagram.png)

**ORM and Entities (example):** In the database, order are stored in ... that are mapped an `Order` entity. The `Order` ↔ `OrderItem` relationship ... ensures that an `Order` has at least one `OrderItem` and an `OrderItem` always relates to an `Order`.

---

## ✅ Project Requirements

---
Each app must meet the following criteria in order to be accepted (see also the official project guidelines PDF on Moodle):

1. Using NiceGUI for building an interactive web app
2. Data validation in the app
3. Using an ORM for database management

---

### 1. Browser-based App (NiceGUI)

> 🚧 In this section, document how your project fulfills each criterion.

The application interacts with the user via the browser. Users can:

- View the pizza menu
- Select pizzas and quantities
- See the running total
- Receive an invoice generated as a file

**Architecture note (per SS26 guidelines):** the browser is a thin client; UI state + business logic live on the server-side NiceGUI app.

---

### 2. Data Validation

The application validates all user input to ensure data integrity and a smooth user experience.
These checks prevent crashes and guide the user to provide correct input, matching the validation requirements described in the project guidelines.

---

### 3. Database Management

All relevant data is managed via an ORM (e.g. SQLModel or SQLAlchemy). For the pizza example this includes users, pizzas, and orders.

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
pizza-app/
├─ README.md
├─ pyproject.toml
├─ .env.example
├─ .gitignore
│
├─ pizza_app/
│  ├─ __main__.py               # entrypoint (py -m pizza_app)
│  ├─ application.py            # composition root
│  │
│  ├─ domain/
│  │  └─ models.py
│  │
│  ├─ infra/
│  │  ├─ db.py
│  │  ├─ repositories.py
│  │  └─ seed.py
│  │
│  ├─ services/
│  │  ├─ pricing.py
│  │  └─ invoice.py
│  │
│  ├─ ui/
│  │  ├─ pages.py
│  │  └─ controllers.py
│
├─ docs/
│  ├─ ui-images/
│  │  ├─ ui_showcase.png
│  │  ├─ ui_menu.png
│  │  ├─ ui_checkout.png
│  │  ├─ wireframe_home.png
│  │  └─ wireframe_checkout.png
│  │
│  └─ architecture-diagrams/
│     ├─ uml_use_case_diagram.png
│     ├─ uml_class_architecture.png
│     ├─ uml_class_domain.png
│     ├─ uml_class_persistence.png
│     └─ er_diagram.png
│
├─ data/                        # sqlite DB (gitignored)
├─ invoices/                    # generated PDFs (gitignored)
│
└─ tests/
   ├─ conftest.py
   ├─ test_pricing.py
   └─ test_checkout_and_invoice.py
```

---

### How to Run

> 🚧 Adjust to your project.

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
- E.g., setup of parameters or environment variables

### 3. Launch
- Start the NiceGUI app (example):
   ```bash
   py -m pizza_app
   ```
- Open the URL printed in the console.

### 4. Usage (document as steps)

> 🚧 Describe the usage of the main functions

Order Pizza:
1. Open the menu page and browse pizzas.
2. Add items (with quantities) to the current order.
3. Review total (incl. discounts) and validate inputs.
4. Checkout to persist the order and generate the invoice.

> 🚧 Add UI screenshots of the main screens (or a short video link):

![UI – Checkout](docs/ui-images/ui_checkout_screen.png)
![UI – Past Transactions](docs/ui-images/ui_past_transactions_screen.png)

---

## 🧪 Testing

> 🚧 Explain what you test and how to run tests.

**Test mix:**
- Overall 12 tests
- 6 Unit tests: e.g. subtotal calculation, discount application above CHF 50, no discount at or below threshold, total calculation
- 3 DB tests: e.g. menu query returns seeded pizzas, saving an order persists order + order items, empty DB / empty transactions behavior
- 3 Integration tests: e.g. checkout with one pizza creates order and invoice, checkout with multiple pizzas applies discount correctly

**Template for writing test cases**
1. Test case ID – unique identifier (e.g., TC_001)
2. Test case title/description – What is the test about?
3. Preconditions: Requirements before executing the test
4. Test steps: Actions to perform
5. Test data/input
6. Expected result
7. Actual result
8. Status – pass or fail
9. Comments – Additional notes or defect found

**Run:**
```bash
pytest
```

> 🚧 If you provide separate commands, document them here (e.g. `pytest -m integration`).

---

### Libraries Used

- see above

## 👥 Team & Contributions

---

> 🚧 Fill in the names of all team members and describe their individual contributions below.

| Name      | Contribution |
|-----------|--------------|
| Student A | NiceGUI UI + documentation |
| Student B | Database & ORM + documentation |
| Student C | Business logic + documentation |

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

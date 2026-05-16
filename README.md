# University Note-Taking API and Interactive Frontend

Ein robustes, voll funktionsfaehiges Notiz-Verwaltungssystem, entwickelt im Rahmen des Kurses Applied Programming an der TH Coburg. Das Projekt kombiniert ein hochgradig validiertes FastAPI-Backend mit einer persistenten SQLite-Datenbank und einer reaktiven Benutzeroberflaeche auf Streamlit-Basis.

## Kern-Features

### Backend und Datenhaltung (FastAPI und SQLModel)
- Komplette CRUD-Operationen: Erstellen, Lesen, Aktualisieren (PUT/PATCH) und Loeschen von Notizen.
- Relationsdatenbank: Verwendung von SQLModel zur Modellierung von m:n-Beziehungen zwischen Notizen und dynamischen Tags ueber eine Zwischentabelle.
- Persistente Speicherung: Lokale SQLite-Datenbank (notes.db), die Daten auch nach Server-Neustarts sicher aufbewahrt.
- Erweiterte API-Logik: Ein universeller /notes-Endpunkt mit kombinierbaren Query-Parametern fuer Volltextsuche (search), Kategorie-Filterung, Tag-Filterung sowie Datumsbereiche (created_after/created_before).
- Statistik-Engine: Ein /notes/stats-Endpunkt zur Berechnung der Gesamtzahl, Verteilung nach Kategorien und den Top 5 der am haeufigsten genutzten Tags.

### Datensicherheit und Validierung (Pydantic v2 Core Hardening)
- Strikte Eingabe-Kontrolle: Konfiguration via ConfigDict(extra="forbid") zur strikten Ablehnung nicht deklarierter Felder.
- Automatische Datenbereinigung: str_strip_whitespace=True entfernt automatisch fuehrende und nachfolgende Leerzeichen.
- Custom Field und Model Validators: Automatische Normalisierung von Kategorien und Tags in Kleinbuchstaben. Case-insensitive Deduplizierung von Tags. Cross-Field Validation, die verhindert, dass Titel und Inhalt identisch sind.
- Advanced Types (Stretch Goals): Integration von EmailStr fuer die Autoren-E-Mail und Wertebereichsueberwachung (ge=1, le=5) fuer die Priorisierung von Notizen.

### Frontend (Streamlit Web-UI)
- Moderne 2-Spalten-Architektur: Linke Spalte fuer die Anzeige gespeicherter Notizen, rechte Spalte fuer die Datenerfassung.
- Dynamische Datenvisualisierung: Notizen werden in interaktiven Expandern dargestellt. Tags werden optisch hervorgehoben und Prioritaeten intuitiv als Sterne-Rating (⭐) visualisiert.
- Sichere Formular-Uebertragung: Nutzung von st.form, um Eingaben zu buendeln und gesammelt per POST-Request an das Backend zu uebergeben.
- Robustes Error Handling: Abfangen von Verbindungsabbruechen (ConnectionError) mit benutzerfreundlichen Statusmeldungen statt Python-Tracebacks.

## Installation und Setup

### Voraussetzungen
- Python 3.13+
- Installed uv Package Manager

### Repository synchronisieren
cd appliedprogrammingproject
uv sync

## Anwendung starten

Das Backend und das Frontend muessen in zwei separaten Terminal-Fenstern parallel gestartet werden:

### Terminal 1: FastAPI Backend
uv run fastapi dev

- API-Server laeuft unter: http://127.0.0.1:8000
- Interaktive Swagger-Dokumentation: http://127.0.0.1:8000/docs
- Alternative ReDoc-Dokumentation: http://127.0.0.1:8000/redoc

### Terminal 2: Streamlit Frontend
uv run streamlit run frontend.py

- Web-Oberflaeche laeuft unter: http://localhost:8501

## API-Endpunkt-Uebersicht

### 1. Basis- und Demorouten (Tag 1)
- GET / - HelloWorld Status-Meldung
- GET /status - Liefert Online-Status, API-Version und aktuellen Kurstag
- GET /about - Projekt- und Autoren-Informationen
- GET /student - Profildaten des Studierenden (Ilia Beliaev)
- GET /square/{number} - Mathematische Berechnung: Quadratzahl
- GET /double/{number} - Mathematische Berechnung: Verdopplung

### 2. Notizen-Verwaltung (Core REST API)
- POST /notes - Erstellt eine neue Notiz (inkl. Pydantic-Validierung)
- GET /notes - Listet alle Notizen (Unterstuetzt Filter: category, search, tag, created_after, created_before)
- GET /notes/{note_id} - Ruft eine spezifische Notiz anhand ihrer ID ab
- PUT /notes/{note_id} - Vollstaendige Aktualisierung (Ersetzt die Ressource)
- PATCH /notes/{note_id} - Teilweise Aktualisierung (Aktualisiert nur uebergebene Felder)
- DELETE /notes/{note_id} - Loescht eine Notiz aus der Datenbank (Status 204)

### 3. Meta- und Analysedaten
- GET /notes/stats - Berechnet globale Statistiken (Total, Kategorien, Top-Tags)
- GET /tags - Listet alle in der Datenbank existierenden Tags (sortiert)
- GET /categories - Listet alle aktuell genutzten Kategorien auf

## Interaktions-Beispiele

### Neue Notiz anlegen (POST-Request)
curl -X POST http://127.0.0.1:8000/notes -H accept:application/json -H Content-Type:application/json -d {"title":"Klausurvorbereitung","content":"Kapitel 1 bis 7 wiederholen.","category":"study","tags":["python","fastapi"],"priority":5,"author_email":"ilia.beliaev@stud.hs-coburg.de"}

### Komplexe Filter-Kombinationen (GET-Request)
- Suche in Kategorie: GET /notes?category=study&search=FastAPI
- Filter nach Tag: GET /notes?tag=python
- Filter nach Erstellungsdatum: GET /notes?created_after=2026-01-01T00:00:00

## Testing
Ausfuehrung der lokalen Tests gegen die Kurs-Testsuite via Terminal:
uv run pytest -v

## Technologie-Stack
- Backend Framework: FastAPI (ASGI)
- Datenbank-Layer (ORM): SQLModel und SQLAlchemy
- Datenbank: SQLite (In-File Persistence)
- Validierungs-Engine: Pydantic v2 (Hardened Constraints)
- Frontend-GUI: Streamlit (Reactive Framework)
- Paketmanagement: uv (Astral)
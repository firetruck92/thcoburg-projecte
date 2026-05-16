# University Note-Taking API & Interactive Frontend

Ein robustes, voll funktionsfähiges Notiz-Verwaltungssystem, entwickelt im Rahmen des Kurses Applied Programming an der TH Coburg. Das Projekt kombiniert ein hochgradig validiertes FastAPI-Backend mit einer persistenten SQLite-Datenbank und einer reaktiven Benutzeroberfläche auf Streamlit-Basis.

## Kern-Features

### Backend & Datenhaltung (FastAPI & SQLModel)
- Komplette CRUD-Operationen: Nahtloses Erstellen, Lesen, Aktualisieren (PUT/PATCH) und Löschen von Notizen.
- Relationsdatenbank: Verwendung von SQLModel (basiert auf SQLAlchemy) zur Modellierung von m:n-Beziehungen zwischen Notizen und dynamischen Tags über eine Zwischentabelle.
- Persistente Speicherung: Lokale SQLite-Datenbank (notes.db), die Daten auch nach Server-Neustarts sicher aufbewahrt.
- Erweiterte API-Logik: Ein universeller /notes-Endpunkt mit kombinierbaren Query-Parametern für Volltextsuche (search), Kategorie-Filterung und Tag-Filterung.
- Statistik-Engine: Ein /notes/stats-Endpunkt zur Berechnung der Gesamtzahl, Verteilung nach Kategorien und den Top 5 der am häufigsten genutzten Tags.

### Datensicherheit & Validierung (Pydantic v2 Core Hardening)
- Strikte Eingabe-Kontrolle: Konfiguration via ConfigDict(extra="forbid") zur strikten Ablehnung nicht deklarierter Felder.
- Automatische Datenbereinigung: str_strip_whitespace=True entfernt automatisch führende/nachstehende Leerzeichen.
- Custom Field & Model Validators: Automatische Normalisierung von Kategorien und Tags in Kleinbuchstaben (lowercase). Case-insensitive Deduplizierung von Tags direkt bei der Übertragung. Cross-Field Validation als Schutzregel, die verhindert, dass Titel und Inhalt identisch sind.
- Advanced Types & Boundaries (Stretch Goals): Integration von EmailStr für die optionale Autoren-E-Mail und Wertebereichsüberwachung (ge=1, le=5) für die Priorisierung von Notizen.

### Frontend (Streamlit Web-UI)
- Moderne 2-Spalten-Architektur: Linke Spalte für die interaktive Anzeige, rechte Spalte für die Datenerfassung.
- Dynamische Datenvisualisierung: Notizen werden übersichtlich in interaktiven Akkordeons dargestellt. Tags werden optisch hervorgehoben und Prioritäten intuitiv als Sterne-Rating (⭐) visualisiert.
- Sichere Formular-Übertragung: Nutzung von st.form, um Eingaben zu bündeln und gesammelt per POST-Request fehlerfrei an das Backend zu übergeben.
- Robustes Error Handling: Abfangen von Verbindungsabbrüchen (ConnectionError) mit benutzerfreundlichen Statusmeldungen statt Python-Tracebacks.

## Installation und Setup

### Voraussetzungen
- Python 3.13+
- Installed uv Package Manager (empfohlen für das Kurs-Umfeld)

### Repository synchronisieren
```bash
cd appliedprogrammingproject
uv sync

Anwendung starten

Um das vollständige System zu nutzen, müssen das Backend und das Frontend in zwei separaten Terminal-Fenstern parallel gestartet werden:
Terminal 1: FastAPI Backend
Bash

uv run fastapi dev

    API-Server läuft unter: http://127.0.0.1:8000

    Interaktive Swagger UI Dokumentation: http://127.0.0.1:8000/docs

    ReDoc alternative Dokumentation: http://127.0.0.1:8000/redoc

Terminal 2: Streamlit Frontend
Bash

uv run streamlit run frontend.py

    Web-Oberfläche öffnet sich automatisch unter: http://localhost:8501

API-Endpunkt-Übersicht
1. Basis- & Demorouten (Tag 1)

    GET / - HelloWorld Status-Meldung

    GET /status - Liefert Online-Status, API-Version und aktuellen Kurstag

    GET /about - Projekt- und Autoren-Informationen

    GET /student - Profildaten des Studierenden (Daria Yeromina)

    GET /square/{number} - Mathematische Berechnung: Quadratzahl

    GET /double/{number} - Mathematische Berechnung: Verdopplung

2. Notizen-Verwaltung (Core REST API)

    POST /notes - Erstellt eine neue Notiz (inkl. Pydantic-Validierung)

    GET /notes - Listet alle Notizen (Unterstützt Filter: category, search, tag)

    GET /notes/{note_id} - Ruft eine spezifische Notiz anhand ihrer ID ab

    PUT /notes/{note_id} - Vollständige Aktualisierung (Ersetzt die Ressource)

    PATCH /notes/{note_id} - Teilweise Aktualisierung (Aktualisiert nur übergebene Felder)

    DELETE /notes/{note_id} - Löscht eine Notiz unwiderruflich aus der Datenbank (Status 204)

3. Meta- & Analysedaten

    GET /notes/stats - Berechnet globale Statistiken (Total, Kategorien, Top-Tags)

    GET /tags - Listet alle in der Datenbank existierenden Tags (sortiert)

    GET /categories - Listet alle aktuell genutzten Kategorien auf

Interaktions-Beispiele (CURL & Filtering)
Neue Notiz anlegen (POST-Request)
Bash

curl -X 'POST' \
  '[http://127.0.0.1:8000/notes](http://127.0.0.1:8000/notes)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{\n  "title": "Klausurvorbereitung",\n  "content": "Angewandte Programmierung Kapitel 1 bis 7 wiederholen.",\n  "category": "Study",\n  "tags": ["Python", "FastAPI", "Python"],\n  "priority": 5,\n  "author_email": "daria.yeromina@stud.hs-coburg.de"\n}'

Hinweis zur automatischen Bereinigung: Das Tag "Python" wird dedupliziert, die Kategorie "Study" wird automatisch als "study" abgespeichert.
Komplexe Filter-Kombinationen (GET-Request)

    Nur Notizen della Kategorie "study" durchsuchen, die das Wort "FastAPI" enthalten: GET /notes?category=study&search=FastAPI

    Nach einem bestimmten Tag filtern: GET /notes?tag=python

Testing

Das Backend wurde intensiv gegen die offizielle, von der Kursleitung bereitgestellte Test-Suite geprüft. Alle funktionalen Anforderungen, Edge Cases und erwarteten Statuscodes (201, 204, 404, 422) werden fehlerfrei erfüllt.

Ausführung der lokalen Tests:
Bash

uv run pytest -v

Technologie-Stack

    Backend Framework: FastAPI (Asynchronous Server Gateway Interface)

    Datenbank-Layer (ORM): SQLModel & SQLAlchemy

    Datenbank: SQLite (In-File Persistence)

    Validierungs-Engine: Pydantic v2 (Hardenend & Constraints)

    Frontend-GUI: Streamlit (Reactive Framework)

    Paketmanagement: uv (Astral)
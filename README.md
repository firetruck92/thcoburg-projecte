University Note-Taking API and Interactive Frontend

Ein robustes, voll funktionsfaehiges Notiz-Verwaltungssystem, entwickelt im Rahmen des Kurses Applied Programming an der TH Coburg. Das Projekt kombiniert ein hochgradig validiertes FastAPI-Backend mit einer persistenten SQLite-Datenbank und einer reaktiven Benutzeroberflaeche auf Streamlit-Basis.
Kern-Features
Backend und Datenhaltung (FastAPI und SQLModel)

    Komplette CRUD-Operationen: Erstellen, Lesen, Aktualisieren (PUT/PATCH) und Loeschen von Notizen.

    Relationsdatenbank: Verwendung von SQLModel zur Modellierung von m:n-Beziehungen zwischen Notizen und dynamischen Tags ueber eine Zwischentabelle.

    Persistente Speicherung: Lokale SQLite-Datenbank (notes.db), die Daten auch nach Server-Neustarts sicher aufbewahrt.

    Erweiterte API-Logik: Ein universeller /notes-Endpunkt mit kombinierbaren Query-Parametern fuer Volltextsuche (search), Kategorie-Filterung und Tag-Filterung.

    Statistik-Engine: Ein /notes/stats-Endpunkt zur Berechnung der Gesamtzahl, Verteilung nach Kategorien und den Top 5 der am haeufgsten genutzten Tags.

Datensicherheit und Validierung (Pydantic v2)

    Strikte Eingabe-Kontrolle: Konfiguration via ConfigDict(extra="forbid") zur strikten Ablehnung nicht deklarierter Felder.

    Automatische Datenbereinigung: str_strip_whitespace=True entfernt automatisch Leerzeichen.

    Custom Field und Model Validators: Automatische Normalisierung von Kategorien und Tags in Kleinbuchstaben. Case-insensitive Deduplizierung von Tags. Cross-Field Validation, die verhindert, dass Titel und Inhalt identisch sind.

    Advanced Types (Stretch Goals): Integration von EmailStr fuer die Autoren-E-Mail und Wertebereichsueberwachung (ge=1, le=5) fuer die Priorisierung von Notizen.

Frontend (Streamlit Web-UI)

    Moderne 2-Spalten-Architektur: Linke Spalte fuer die Anzeige, rechte Spalte fuer die Datenerfassung.

    Dynamische Datenvisualisierung: Notizen werden in interaktiven Expandern dargestellt. Tags werden optisch hervorgehoben und Prioritaeten intuitiv als Sterne-Rating visualisiert.

    Sichere Formular-Uebertragung: Nutzung von st.form, um Eingaben zu buendeln und gesammelt per POST-Request an das Backend zu uebergeben.

Installation und Setup
Voraussetzungen

    Python 3.13+

    Installed uv Package Manager

Repository synchronisieren

cd appliedprogrammingproject
uv sync
Anwendung starten

Das Backend und das Frontend muessen in zwei separaten Terminal-Fenstern parallel gestartet werden:
Terminal 1: FastAPI Backend

uv run fastapi dev

    API-Server laeuft unter: http://127.0.0.1:8000

    Dokumentation: http://127.0.0.1:8000/docs

Terminal 2: Streamlit Frontend

uv run streamlit run frontend.py

    Web-Oberflaeche laeuft unter: http://localhost:8501

API-Endpunkt-Uebersicht
1. Basis-Routen

    GET / - HelloWorld Status-Meldung

    GET /status - Liefert Online-Status, API-Version und aktuellen Kurstag

    GET /about - Projekt- und Autoren-Informationen

    GET /student - Profildaten des Studierenden (Dein Name)

    GET /square/{number} - Mathematische Berechnung: Quadratzahl

    GET /double/{number} - Mathematische Berechnung: Verdopplung

2. Notizen-Verwaltung

    POST /notes - Erstellt eine neue Notiz

    GET /notes - Listet alle Notizen (Filter: category, search, tag)

    GET /notes/{note_id} - Ruft eine spezifische Notiz anhand ihrer ID ab

    PUT /notes/{note_id} - Vollstaendige Aktualisierung

    PATCH /notes/{note_id} - Teilweise Aktualisierung

    DELETE /notes/{note_id} - Loescht eine Notiz (Status 204)

3. Meta-Daten

    GET /notes/stats - Berechnet globale Statistiken

    GET /tags - Listet alle existierenden Tags

    GET /categories - Listet alle aktuell genutzten Kategorien auf

Interaktions-Beispiele
Neue Notiz anlegen (POST)

curl -X POST http://127.0.0.1:8000/notes -H accept:application/json -H Content-Type:application/json -d {"title":"Klausurvorbereitung","content":"Kapitel 1 bis 7 wiederholen.","category":"study","tags":["python","fastapi"],"priority":5,"author_email":"deine.email@stud.hs-coburg.de"}
Filter-Kombinationen (GET)

    Suche in Kategorie: GET /notes?category=study&search=FastAPI

    Filter nach Tag: GET /notes?tag=python

Testing

Ausfuehrung der lokalen Tests via Terminal:
uv run pytest -v
Technologie-Stack

    Backend Framework: FastAPI

    Datenbank-Layer: SQLModel und SQLAlchemy

    Datenbank: SQLite

    Validierungs-Engine: Pydantic v2

    Frontend-GUI: Streamlit

    Paketmanagement: uv
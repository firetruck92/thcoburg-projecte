# University Note-Taking API & Interactive Frontend

Ein robustes, voll funktionsfähiges Notiz-Verwaltungssystem, entwickelt im Rahmen des Kurses **Applied Programming** an der **TH Coburg**. Das Projekt kombiniert ein hochgradig validiertes FastAPI-Backend mit einer persistenten SQLite-Datenbank und einer reaktiven Benutzeroberfläche auf Streamlit-Basis.

## 🚀 Kern-Features

### 🗄️ Backend & Datenhaltung (FastAPI & SQLModel)
- **Komplette CRUD-Operationen:** Nahtloses Erstellen, Lesen, Aktualisieren (PUT/PATCH) und Löschen von Notizen.
- **Relatonsdatenbank:** Verwendung von **SQLModel** (basiert auf SQLAlchemy) zur Modellierung von m:n-Beziehungen zwischen Notizen und dynamischen Tags über eine Zwischentabelle (`notetaglink`).
- **Persistente Speicherung:** Lokale SQLite-Datenbank (`notes.db`), die Daten auch nach Server-Neustarts sicher aufbewahrt.
- **Erweiterte API-Logik:** Ein universeller `/notes`-Endpunkt mit kombinierbaren Query-Parametern für Volltextsuche (`search`), Kategorie-Filterung und Tag-Filterung.
- **Statistik-Engine:** Ein `/notes/stats`-Endpunkt zur Berechnung der Gesamtzahl, Verteilung nach Kategorien und den Top 5 der am häufigsten genutzten Tags.

### 🛡️ Datensicherheit & Validierung (Pydantic v2 Core Hardening)
- **Strikte Eingabe-Kontrolle:** Konfiguration via `ConfigDict(extra="forbid")` zur strikten Ablehnung nicht deklarierter Felder.
- **Automatische Datenbereinigung:** `str_strip_whitespace=True` entfernt automatisch führende/nachstehende Leerzeichen.
- **Custom Field & Model Validators:** - Automatische Normalisierung von Kategorien und Tags in Kleinbuchstaben (`lowercase`).
  - Case-insensitive Deduplizierung von Tags direkt bei der Übertragung.
  - Cross-Field Validation: Schutzregel, die verhindert, dass Titel und Inhalt identisch sind.
- **Advanced Types & Boundaries (Stretch Goals):** Integration von `EmailStr` für die optionale Autoren-E-Mail und Wertebereichsüberwachung (`ge=1, le=5`) für die Priorisierung von Notizen.

### 🎨 Frontend (Streamlit Web-UI)
- **Moderne 2-Spalten-Architektur:** Linke Spalte für die interaktive Anzeige, rechte Spalte für die Datenerfassung.
- **Dynamische Datenvisualisierung:** Notizen werden übersichtlich in interaktiven Akkordeons (`st.expander`) dargestellt. Tags werden optisch hervorgehoben und Prioritäten intuitiv als Sterne-Rating (`⭐`) visualisiert.
- **Sichere Formular-Übertragung:** Nutzung von `st.form`, um Eingaben zu bündeln und gesammelt per POST-Request fehlerfrei an das Backend zu übergeben.
- **Robustes Error Handling:** Abfangen von Verbindungsabbrüchen (`ConnectionError`) mit benutzerfreundlichen Statusmeldungen statt Python-Tracebacks.

---

## 🛠️ Installation und Setup

### Voraussetzungen
- **Python 3.13+**
- Installed **`uv` Package Manager** (empfohlen für das Kurs-Umfeld)

### Repository synchronisieren
```bash
# In das Projektverzeichnis wechseln
cd appliedprogrammingproject

# Abhängigkeiten via uv installieren
uv sync
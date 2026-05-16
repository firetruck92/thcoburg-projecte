# Work Log

**Student Name:Ilia Beliaev** 

Instructions: Fill out one log for each course day. Content to consider: Course Sessions + Assignment

## Template:

---

## 1. ✅ What did I accomplish?

_Reflect on the activities, exercises, and work you completed today._

**Guiding questions:**
- What topics or concepts did you work with?
- What exercises or projects did you complete?
- What tools or technologies did you use?
- What did you learn or practice?



---

## 2. 🚧 What challenges did I face?

_Describe any difficulties, obstacles, or confusing moments you encountered._

**Guiding questions:**
- What was difficult to understand?
- Where did you get stuck?
- What errors or problems did you face?
- What felt frustrating or confusing?




---

## 3. 💡 How did I overcome them?

_Explain how you overcame the challenges or what help you needed._

**Guiding questions:**
- What strategies did you try?
- Who or what helped you (instructor, classmates, documentation)?
- What did you learn from solving the problem?
- What questions do you still have?


---

## Week 1

### Day 1

#### 1. ✅ What did I accomplish?

Konzepte: Client-Server-Modell, HTTP-Requests, REST-APIs und JSON-Struktur gelernt.

Tools: Git (Versionsverwaltung), VS Code (Editor) und uv (Package-Manager) eingerichtet.

Code: Eine FastAPI-App mit 6 Endpunkten geschrieben:

    Basis-Endpunkte: /, /status, /about.

    Hausaufgabe: /square/{number}, /double/{number} und /student (Studentenprofil).

Testen: Alle Endpunkte erfolgreich über die automatische Swagger-UI (/docs) getestet.

---

#### 2. 🚧 What challenges did I face?

Git-Konfiguration: Beim ersten Versuch zu committen, hat Git den Prozess abgebrochen, weil user.name und user.email im System noch nicht global hinterlegt waren.

---

#### 3. 💡 How did I overcome them?


Schneller Fix: Ich habe das Problem direkt über das Terminal mit zwei Befehlen gelöst:
git config --global user.name "Mein Name"
git config --global user.email "meine@email.com"
Danach lief der Commit sofort ohne Probleme durch.

---

### Day 2

#### 1. ✅ What did I accomplish?

Konzepte: Datentypen in Python vertieft sowie den Unterschied zwischen HTTP GET (Daten abrufen) und HTTP POST (Daten senden) gelernt. Das Prinzip der Daten-Persistenz verstanden.

Tools: Eine .gitignore-Datei für Python-Projekte eingerichtet, um temporäre Dateien vom Git-Tracking auszuschließen.

Code: Das API aus der Vorlesung um drei Hausaufgaben-Features erweitert:

    Das Datenmodell (Pydantic) angepasst: Jede Notiz besitzt nun das Pflichtfeld category.

    Filter-Endpunkt gebaut: /notes/category/{category} gibt gezielt Notizen einer bestimmten Kategorie aus.

    Statistik-Endpunkt gebaut: /notes/stats liefert die Gesamtzahl der Notizen sowie die Verteilung pro Kategorie.

Persistenz: Die Notizen werden permanent in einer lokalen JSON-Datei (data/notes.json) gespeichert und bleiben auch nach einem Server-Neustart erhalten.

---

#### 2. 🚧 What challenges did I face?

JSON-Serialisierung: Beim ersten Versuch, die Notizen in die Datei zu schreiben, traten Fehler auf. Pydantic-Modellobjekte können von der Standardbibliothek json.dump() nicht direkt verarbeitet werden, da sie keine nativen Python-Dictionaries sind.

Ordnerstruktur: Es gab anfangs Probleme beim automatischen Erstellen des data/-Verzeichnisses, wenn die JSON-Datei noch nicht existierte.

---

#### 3. 💡 How did I overcome them?
Datentyp-Konvertierung: Das Problem wurde durch die Verwendung der Methode .model_dump() gelöst. Damit werden die Pydantic-Objekte vor dem Speichern in reguläre Python-Dictionaries umgewandelt.

Pfad-Erstellung: Mit Path("data/notes.json").parent.mkdir(parents=True, exist_ok=True) wurde sichergestellt, dass der übergeordnete Ordner vor dem Schreibvorgang automatisch generiert wird.

Offene Frage: Wie kann man bestehende Einträge im JSON-File über ein HTTP PUT- oder DELETE-Request nachträglich modifizieren oder komplett entfernen?
---

### Day 3

#### 1. ✅ What did I accomplish?
Konzepte: Das REST-Architekturkonzept (Ressourcenorientierung, semantische Nutzung von HTTP-Methoden und korrekte Statuscodes) verstanden und umgesetzt. Den Unterschied zwischen Pfad-Parametern zur Ressourcenidentifikation und Query-Parametern zur Filterung gelernt.

Datenbank-Migration: Das Speichersystem komplett von unzuverlässigen JSON-Dateien auf eine relationale SQLite-Datenbank unter Verwendung von SQLModel (Kombination aus Pydantic und SQLAlchemy) umgestellt.

Code & CRUD-Ausbau: Die API zu einem vollständigen CRUD-System erweitert:

    PUT /notes/{id} für den vollständigen Austausch einer Notiz.

    PATCH /notes/{id} für partielle, feldspezifische Updates von Attributen.

    DELETE /notes/{id} mit dem Statuscode 204 No Content zum dauerhaften Löschen.

Beziehungen & Filter: Eine Many-to-Many-Beziehung für flexible tags über eine Verknüpfungstabelle implementiert. Dedizierte relationale Endpunkte wie /tags/{name}/notes und /categories/{name}/notes hinzugefügt.

Advanced Features: Komplexe kombinierte Filterung, ISO-basierte Datumsbereichsfilter (created_after/created_before) sowie eine erweiterte Statistik über Pythons collections.Counter-Modul zur Ermittlung der Top-5-Tags integriert.
---

#### 2. 🚧 What challenges did I face?
Many-to-Many-Beziehungen: Das Aufsetzen der Verknüpfungstabelle (NoteTagLink) in SQLModel und das Auflösen von zirkulären Abhängigkeiten bei der Datenausgabe waren anfangs komplex zu strukturieren.

Datenbank-Sitzungen: Verständnisprobleme bei der korrekten Weitergabe und Schließung der Datenbanksitzung (SessionDep) via Dependency Injection an die einzelnen Endpunkte.

Typkonvertierung bei der API-Antwort: SQLModel-Objekte ließen sich aufgrund geladener Beziehungsdaten nicht direkt serialisieren, was zu Fehlern bei der JSON-Rückgabe führte.
---

#### 3. 💡 How did I overcome them?
Link-Modell-Definition: Die Tabellenstruktur wurde exakt nach der SQLModel-Dokumentation mit link_model=NoteTagLink definiert, was die M2M-Tabelle im Hintergrund fehlerfrei generiert.

Dediizierte Response-Modelle: Zur sauberen Trennung von Datenbank- und API-Schicht wurden Pydantic-Response-Modelle (NoteResponse) definiert. Die Daten werden vor der Rückgabe explizit konvertiert, um Serialisierungsfehler zu vermeiden.

Integrierte Module: Die Aggregation der am häufigsten genutzten Tags im Statistik-Endpunkt wurde effizient über Pythons integriertes collections.Counter-Modul gelöst, statt eigene Sortieralgorithmen zu schreiben.
---

## Week 2

### Day 4

#### 1. ✅ What did I accomplish?
- **Konzepte:** Das Zusammenspiel zwischen HTTP-POST-Anfragen, Request-Bodies und automatischer Datenvalidierung vertieft. Gelernt, wie man fehlerhafte Eingaben direkt an der API-Schnittstelle abfängt.
- **Pydantic Field Constraints:** Die ersten expliziten Validierungsregeln mithilfe von Pydantic `Field(...)` implementiert. Constraints wie `min_length` und `max_length` wurden für die Felder `title`, `content` und `category` definiert, um die Konsistenz der Datenbasis zu sichern.
- **Einführung in pytest:** Erste automatisierte Unittests mit `pytest` geschrieben. Dabei das fundamentale Prinzip "Arrange-Act-Assert" angewendet, um sowohl erfolgreiche Abläufe (201 Created) als auch Validierungsfehler (422 Unprocessable Entity) strukturiert zu prüfen.

---
#### 2. 🚧 What challenges did I face?
- **Test-Isolierung:** Beim Testen von POST-Endpoints veränderten die Testläufe die echten persistenten Daten, was zu Seiteneffekten bei aufeinanderfolgenden Testausführungen führte.
- **Fehlermeldungen interpretieren:** Die verschachtelte Struktur der von FastAPI automatisch generierten 422-Validierungsfehler im JSON-Format war anfangs schwer zu analysieren.

---
#### 3. 💡 How did I overcome them?
- **Bereinigung der Testumgebung:** Für die Testläufe wurde eine temporäre Logik bzw. Bereinigung integriert, um sicherzustellen, dass die Tests reproduzierbar bleiben und die produktive Datenbasis nicht korrumpieren.
- **Dokumentationsanalyse:** Durch intensives Testen der Endpunkte in der interaktiven Swagger-UI (`/docs`) konnten die Pydantic-Fehlermeldungen Schritt für Schritt nachvollzogen und im Testcode präzise per Assertions überprüft werden. 

### Day 5

#### 1. ✅ What did I accomplish?
- **Konzepte:** Das Prinzip der tiefgehenden, datenzentrierten Validierung verstanden. Komplexe Geschäftsregeln (Cross-Field Validation) wurden direkt in die Pydantic-Modelle ausgelagert, um den Endpoint-Code schlank und wartbar zu halten.
- **Modell-Absicherung (Core Hardening):** Die Datensicherheit durch Konfiguration des `ConfigDict` maximiert. Mittels `extra="forbid"` werden nicht deklarierte Felder in Requests strikt blockiert. Dank `str_strip_whitespace=True` werden führende und nachstehende Leerzeichen automatisch entfernt.
- **Erweiterte Validatoren:** Custom `@field_validator`-Funktionen zur automatischen String-Normalisierung (Kategorien werden immer in Kleinbuchstaben umgewandelt) und zur case-insensitiven Deduplizierung von Tags implementiert. Zudem einen `@model_validator(mode="after")` hinzugefügt, um zu verhindern, dass Titel und Inhalt identisch sind.
- **Stretch Goals:** Die Modelle um fortgeschrittene Datentypen erweitert: Einbindung des Typs `EmailStr` für ein optionales `author_email`-Feld sowie numerische Wertebereichsüberwachung (`ge=1, le=5`) für das Feld `priority`.

---
#### 2. 🚧 What challenges did I face?
- **Datenbank-Migration:** Durch das Hinzufügen der neuen Pflichtfelder aus den Stretch Goals (`priority` und `author_email`) kam es zu Inkompatibilitäten mit der bestehenden SQLite-Struktur, da alte Tabelleneinträge diese Spalten nicht besaßen.

---
#### 3. 💡 How did I overcome them?
- **Schema-Reset:** Die lokale Datenbankdatei `notes.db` wurde manuell gelöscht. Beim anschließenden Neustart des FastAPI-Servers generierte SQLModel das Datenbankschema mitsamt allen neuen Feldern, Validierungen und Tabellenbeziehungen komplett neu und fehlerfrei.

### Day 6

#### 1. ✅ What did I accomplish?
- **Konzepte:** Die fundamentale Bedeutung von umfassenden Regressionstests in echten Softwareprojekten verstanden. Tests sichern ab, dass tiefgreifende Refactorings am Backend keine bestehenden API-Funktionalitäten unbemerkt zerstören.
- **Integration der Test-Suite:** Die offizielle, von der Kursleitung bereitgestellte Test-Suite erfolgreich in das Projektverzeichnis integriert und via Pytest ausgeführt.
- **Code-Refactoring:** Das gesamte Backend (`main.py`) und die zugrundeliegenden Pydantic-Modelle akribisch optimiert und angepasst, bis alle vordefinierten, strengen Testfälle der externen Suite fehlerfrei durchliefen.
- **Robustheit:** Die API garantiert nun auch unter extremen Testbedingungen (Edge Cases, ungültige Datentypen, SQL-Grenzwerte) exakt die erwarteten HTTP-Statuscodes (200, 201, 404, 422).

---
#### 2. 🚧 What challenges did I face?
- **Strikte Vorgaben:** Einige Testfälle der offiziellen Suite erwarteten hochspezifische Feldbezeichnungen, exakte Verschachtelungen und exaktes Verhalten bei unzulässigen Extra-Feldern, was anfangs zu zahlreichen fehlschlagenden Assertions führte.

---
#### 3. 💡 How did I overcome them?
- **Gezielte Fehleranalyse:** Die Testausführung wurde mit detaillierten Flags (`pytest -v`) analysiert. Durch das systematische Abarbeiten der Fehlermeldungen wurden kleine Abweichungen im Validierungsprozess des Backends korrigiert (z. B. exakte Einhaltung der Lowercase-Logik), bis die gesamte Test-Suite vollständig "grün" war.

## Week 3

### Day 7

#### 1. ✅ What did I accomplish?
- **Konzepte:** Das Client-Server-Modell und die Entkopplung von Backend (FastAPI REST-API) und Frontend (Benutzeroberfläche) in einer realen Systemarchitektur verstanden. Die Kommunikation erfolgt sauber über asynchrone HTTP-Requests mittels der `requests`-Bibliothek.
- **UI-Entwicklung mit Streamlit:** Das Streamlit-Framework erlernt und genutzt, um schnell und effizient reaktive Web-Applikationen direkt in Python zu bauen.
- **Frontend-Features:** Eine vollständige Web-Oberfläche (`frontend.py`) implementiert, die zwei Hauptfunktionen erfüllt:
  - **Funktion 1 (Read):** Dynamisches Abrufen aller Notizen aus der SQLite-Datenbank und übersichtliche Darstellung der Inhalte, Tags, E-Mails und Sterne-Prioritäten in interaktiven Akkordeon-Komponenten (`st.expander`).
  - **Funktion 2 (Create):** Ein sicheres Eingabeformular (`st.form`), das Eingaben (Titel, Inhalt, Kategorie, Priorität, E-Mail, Tags) bündelt, validiert und gesammelt per POST-Request an das Backend übermittelt.

---
#### 2. 🚧 What challenges did I face?
- **Asynchroner UI-Zustand:** Nach dem erfolgreichen Absenden des Formulars wurden neu angelegte Notizen in der linken Spalte nicht sofort angezeigt, da Streamlit die Ansicht nicht automatisch aktualisierte.
- **Verbindungsstabilität:** Wenn das FastAPI-Backend während der Frontend-Nutzung gestoppt wurde, stürzte die Streamlit-App mit einem unschönen, kritischen Python-Traceback ab.

---
#### 3. 💡 How did I overcome them?
- **State-Refresh:** Durch den gezielten Einsatz von `st.rerun()` unmittelbar nach dem Erhalt des Erfolgs-Statuscodes `201 Created` vom Server wurde ein sofortiges Neuladen der UI erzwungen.
- **Robustes Error Handling:** Die HTTP-Anfragen wurden in `try-except`-Blöcke verpackt (`requests.exceptions.ConnectionError`). Statt eines Absturzes zeigt das Frontend dem Benutzer nun eine benutzerfreundliche Warnmeldung an, dass der Backend-Server gestartet werden muss.

### Day 8

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

### Day 9

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---


# 🎉 Congratulations! You did it! 🎓✨













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






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

## Week 2

### Day 4

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

### Day 5

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

### Day 6

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

## Week 3

### Day 7

#### 1. ✅ What did I accomplish?






---

#### 2. 🚧 What challenges did I face?






---

#### 3. 💡 How did I overcome them?






---

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













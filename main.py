from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
from pathlib import Path

# Initialisierung der FastAPI-Anwendung
app = FastAPI(
    title="Combined University API",
    description="Backend-Anwendung für Tag 1 und Tag 2 Hausaufgaben",
    version="2.0.0"
)

# Pfad zur JSON-Datei, in der die Notizen permanent gespeichert werden
NOTES_FILE = Path("data/notes.json")

# ==========================================
# 🚀 TAG 1: BASIS-ENDPUNKTE & RECHNER
# ==========================================

# Standard-Root-Endpunkt zur Überprüfung, ob die API erreichbar ist
@app.get("/")
def read_root():
    return {"message": "Hello World!"}

# Status-Endpunkt gibt die aktuelle API-Version und den Kurstag zurück
@app.get("/status")
def get_status():
    return {
        "status": "online",
        "version": "0.2.0",
        "day": 2
    }

# Info-Endpunkt mit Details zum Projekt, Autor und Kurs
@app.get("/about")
def get_about():
    return {
        "project": "My First API",
        "author": "Ilia Beliaev",
        "course": "Applied Programming"
    }

# Berechnet das Quadrat einer Zahl, die als Pfadparameter übergeben wird
@app.get("/square/{number}")
def calculate_square(number: int):
    result = number * number
    return {
        "number": number,
        "square": result,
        "calculation": f"{number} x {number} = {result}"
    }

# Gibt die statischen Profildaten des Studenten zurück
@app.get("/student")
def get_student():
    return {
        "name": "Ilia Beliaev",
        "semester": 1, 
        "course": "Wirtschaftsinformatik", 
        "university": "TH Coburg"
    }

# Multipliziert die übergebene Zahl mit 2 (Verdopplung)
@app.get("/double/{number}")
def calculate_double(number: int):
    result = number * 2
    return {
        "number": number,
        "double": result,
        "calculation": f"{number} x 2 = {result}"
    }


# ==========================================
# 📝 TAG 2: NOTIZ-API (DATEN-PERSISTENZ)
# ==========================================

# Pydantic-Modell für eingehende Daten beim Erstellen einer Notiz (Hausaufgabe: inklusive 'category')
class NoteCreate(BaseModel):
    title: str
    content: str
    category: str  # Feld für die Notiz-Kategorie (z.B. 'study', 'work')

# Pydantic-Modell für die fertige Notiz in der Datenbank (inklusive ID und Zeitstempel)
class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: str

def load_notes():
    """
    Lädt alle Notizen aus der JSON-Datei.
    Gibt eine Liste von Note-Objekten und den nächsten freien ID-Zähler zurück.
    """
    notes_db = []
    note_id_counter = 1
    
    # Prüfen, ob die Datei existiert, um Fehler zu vermeiden
    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Konvertiert die JSON-Dicts in Pydantic-Modelle
                notes_db = [Note(**note) for note in data]
                
                # Setzt den ID-Zähler auf die höchste vorhandene ID + 1
                if notes_db:
                    note_id_counter = max(note.id for note in notes_db) + 1
            except json.JSONDecodeError:
                # Falls die Datei leer oder fehlerhaft ist, starten wir mit einer leeren Liste
                pass
    return notes_db, note_id_counter

def save_notes(notes_db):
    """
    Speichert die aktuelle Notiz-Liste als formatiertes JSON in der Datei ab.
    """
    # Erstellt den Ordner 'data', falls er noch nicht existiert
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        # model_dump() konvertiert Pydantic-Objekte zurück in Python-Dictionaries
        notes_data = [note.model_dump() for note in notes_db]
        json.dump(notes_data, f, indent=2, ensure_ascii=False)

# HTTP POST: Erstellt eine neue Notiz und speichert sie in der Datei
@app.post("/notes", status_code=201)
def create_note(note: NoteCreate) -> Note:
    """Erstellt eine neue Notiz mit Kategorie und speichert sie permanent ab."""
    notes_db, note_id_counter = load_notes()

    # Erstellung des vollständigen Notiz-Objekts
    new_note = Note(
        id=note_id_counter,
        title=note.title,
        content=note.content,
        category=note.category,
        created_at=datetime.now(timezone.utc).isoformat()
    )

    notes_db.append(new_note)
    save_notes(notes_db) # Speichern in den permanenten Speicher
    return new_note

# HTTP GET: Gibt eine Liste aller gespeicherten Notizen zurück
@app.get("/notes")
def list_notes() -> list[Note]:
    """Gibt eine Liste aller vorhandenen Notizen zurück."""
    notes_db, _ = load_notes()
    return notes_db

# HTTP GET: Sucht eine spezifische Notiz nach ihrer ID
@app.get("/notes/{note_id}")
def get_note(note_id: int) -> Note:
    """Sucht eine spezifische Notiz anhand der ID. Wirft 404, falls nicht gefunden."""
    notes_db, _ = load_notes()
    for note in notes_db:
        if note.id == note_id:
            return note
    
    # Fehlermeldung, falls die ID in der JSON-Datei nicht existiert
    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found"
    )

# HAUSAUFGABE TASK 2: Filtert Notizen nach einer bestimmten Kategorie
@app.get("/notes/category/{category}")
def get_notes_by_category(category: str) -> list[Note]:
    """Filtert und gibt alle Notizen zurück, die einer bestimmten Kategorie entsprechen."""
    notes_db, _ = load_notes()
    # Der Vergleich erfolgt via .lower(), um Case-Sensitivity zu ignorieren
    filtered_notes = [note for note in notes_db if note.category.lower() == category.lower()]
    return filtered_notes

# HAUSAUFGABE TASK 3: Berechnet Statistiken über die Notizen
@app.get("/notes/stats")
def get_notes_stats():
    """Gibt Statistiken aus: Gesamtzahl der Notizen und Anzahl pro Kategorie."""
    notes_db, _ = load_notes()
    
    categories = {}
    for note in notes_db:
        if note.category in categories:
            categories[note.category] += 1
        else:
            categories[note.category] = 1
            
    return {
        "total_notes": len(notes_db),
        "by_category": categories
    }
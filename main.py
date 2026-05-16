from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, Annotated
from collections import Counter
from sqlmodel import SQLModel, Field, Session, create_engine, Relationship, select, or_, col

# =========================================================================
# 🚀 INITIALISIERUNG & CONFIGURATION
# =========================================================================

app = FastAPI(
    title="Ilia Beliaev - University API",
    description="Zentrales Repository für alle Kurstage (Jetzt mit Vollem CRUD & SQLite)",
    version="3.0.0"
)

# SQLite-Datenbank Setup (Tag 3 - Task 6)
DATABASE_URL = "sqlite:///notes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    """Erstellt eine neue Datenbanksitzung für jeden Request und schließt sie danach."""
    with Session(engine) as session:
        yield session

# Type-Alias für saubere Dependency Injection in den Endpunkten
SessionDep = Annotated[Session, Depends(get_session)]


# =========================================================================
# 📅 TAG 1: BASIS-ENDPUNKTE & MATHEMATISCHE BERECHNUNGEN
# =========================================================================

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/status")
def get_status():
    return {"status": "online", "version": "3.0.0", "day": 3}

@app.get("/about")
def get_about():
    return {"project": "University API", "author": "Ilia Beliaev", "course": "Applied Programming"}

@app.get("/square/{number}")
def calculate_square(number: int):
    return {"number": number, "square": number * number}

@app.get("/student")
def get_student():
    return {"name": "Ilia Beliaev", "semester": 1, "course": "Wirtschaftsinformatik", "university": "TH Coburg"}

@app.get("/double/{number}")
def calculate_double(number: int):
    return {"number": number, "double": number * 2}


# =========================================================================
# 🗄️ TAG 3: SQLMODEL DATENBANK-TABELLEN (M2M-RELATIONSHIP)
# =========================================================================

class NoteTagLink(SQLModel, table=True):
    """Verknüpfungstabelle für die Many-to-Many Beziehung zwischen Notizen und Tags."""
    __tablename__ = "notetaglink"
    note_id: Optional[int] = Field(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


class Note(SQLModel, table=True):
    """Datenbankmodell für eine Notiz."""
    __tablename__ = "notes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Beziehung zu Tags über die Link-Tabelle
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTagLink)


class Tag(SQLModel, table=True):
    """Datenbankmodell für einen eindeutigen Tag."""
    __tablename__ = "tags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    
    # Rückbeziehung zu Notizen
    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTagLink)


# Erstellt die Tabellen in 'notes.db', falls sie noch nicht existieren
SQLModel.metadata.create_all(engine)


# =========================================================================
# 📋 TAG 3: PYDANTIC-MODELLE FÜR API INPUT/OUTPUT (VALIDATION)
# =========================================================================

class NoteCreate(BaseModel):
    """Modell für das Erstellen/Ersetzen einer Notiz (POST/PUT)."""
    title: str
    content: str
    category: str
    tags: list[str] = []

class NoteUpdate(BaseModel):
    """Modell für partielle Updates via PATCH (Tag 3 - Task 4)."""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None

class NoteResponse(BaseModel):
    """Standard-Ausgabemodell für Notizen an den Client."""
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str

    class Config:
        from_attributes = True


# =========================================================================
# 🛣️ TAG 3: API-ENDPUNKTE (COMPLETE CRUD & ADVANCED FILTERS)
# =========================================================================

def get_or_create_tags(tag_names: list[str], session: SessionDep) -> list[Tag]:
    """Hilfsfunktion zur case-insensitiven Handhabung und Speicherung von Tags."""
    tag_objects = []
    seen_tags = set()
    
    for name in tag_names:
        clean_name = name.lower().strip()
        if not clean_name or clean_name in seen_tags:
            continue
        seen_tags.add(clean_name)
        
        statement = select(Tag).where(Tag.name == clean_name)
        existing_tag = session.exec(statement).first()
        
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=clean_name)
            session.add(new_tag)
            tag_objects.append(new_tag)
            
    return tag_objects


# CREATE: Eine neue Notiz anlegen (POST)
@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    db_note = Note(title=note.title, content=note.content, category=note.category)
    db_note.tags = get_or_create_tags(note.tags, session)
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], created_at=db_note.created_at.isoformat()
    )


# READ ALL: Liste mit kombinierten Filtern & Datumsbereich (GET)
@app.get("/notes")
def list_notes(
    session: SessionDep,
    category: str = None,
    search: str = None,
    tag: str = None,
    created_after: str = None,   # Tag 3 - Task 5 (ISO-Format z.B. 2026-05-01)
    created_before: str = None   # Tag 3 - Task 5
) -> list[NoteResponse]:
    statement = select(Note)
    
    if category:
        statement = statement.where(Note.category == category)
    if search:
        search_lower = search.lower()
        statement = statement.where(or_(col(Note.title).ilike(f"%{search_lower}%"), col(Note.content).ilike(f"%{search_lower}%")))
    if tag:
        statement = statement.join(Note.tags).where(Tag.name == tag.lower())
        
    notes = session.exec(statement).all()
    
    # Datumsfilterung (String-Vergleich auf ISO-Ebene)
    filtered_notes = []
    for n in notes:
        n_iso = n.created_at.isoformat()
        if created_after and n_iso < created_after:
            continue
        if created_before and n_iso > created_before:
            continue
        filtered_notes.append(n)
        
    return [
        NoteResponse(
            id=n.id, title=n.title, content=n.content, category=n.category,
            tags=[t.name for t in n.tags], created_at=n.created_at.isoformat()
        ) for n in filtered_notes
    ]


# READ ONE: Einzelne Notiz abrufen (GET)
@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], created_at=db_note.created_at.isoformat()
    )


# UPDATE: Komplette Notiz ersetzen (PUT)
@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
        
    db_note.title = note_update.title
    db_note.content = note_update.content
    db_note.category = note_update.category
    db_note.tags = get_or_create_tags(note_update.tags, session)
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], created_at=db_note.created_at.isoformat()
    )


# PARTIAL UPDATE: Felder einzeln anpassen (PATCH - Tag 3 - Task 4)
@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_patch: NoteUpdate, session: SessionDep) -> NoteResponse:
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
        
    if note_patch.title is not None:
        db_note.title = note_patch.title
    if note_patch.content is not None:
        db_note.content = note_patch.content
    if note_patch.category is not None:
        db_note.category = note_patch.category
    if note_patch.tags is not None:
        db_note.tags = get_or_create_tags(note_patch.tags, session)
        
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], created_at=db_note.created_at.isoformat()
    )


# DELETE: Eine Notiz löschen (DELETE)
@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
    session.delete(db_note)
    session.commit()
    return


# STATISTICS: Aggregierte Auswertungen direkt aus der DB (Tag 3 - Task 2)
@app.get("/notes/stats")
def get_notes_stats(session: SessionDep):
    notes = session.exec(select(Note)).all()
    
    categories = {}
    all_tags_list = []
    
    for n in notes:
        categories[n.category] = categories.get(n.category, 0) + 1
        for t in n.tags:
            all_tags_list.append(t.name)
            
    # Top 5 Meistgenutzte Tags via Counter ermitteln
    tag_counts = Counter(all_tags_list)
    top_tags = [{"tag": tag, "count": count} for tag, count in tag_counts.most_common(5)]
    
    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": top_tags,
        "unique_tags_count": len(tag_counts)
    }


# TAG RESSOURCEN (GET ALL TAGS & RELATIONSHIP)
@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    tags = session.exec(select(Tag)).all()
    return sorted([t.name for t in tags])

@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    statement = select(Tag).where(Tag.name == tag_name.lower())
    tag_obj = session.exec(statement).first()
    if not tag_obj:
        return []
    return [
        NoteResponse(
            id=n.id, title=n.title, content=n.content, category=n.category,
            tags=[t.name for t in n.tags], created_at=n.created_at.isoformat()
        ) for n in tag_obj.notes
    ]


# CATEGORY RESSOURCEN (Tag 3 - Task 3)
@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    notes = session.exec(select(Note)).all()
    unique_cats = {n.category for n in notes}
    return sorted(list(unique_cats))

@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str, session: SessionDep) -> list[NoteResponse]:
    statement = select(Note).where(Note.category == category_name)
    notes = session.exec(statement).all()
    return [
        NoteResponse(
            id=n.id, title=n.title, content=n.content, category=n.category,
            tags=[t.name for t in n.tags], created_at=n.created_at.isoformat()
        ) for n in notes
    ]
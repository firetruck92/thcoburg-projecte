from fastapi import FastAPI, HTTPException, Response, Depends
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime
import re
from typing import Optional, Annotated
from sqlmodel import SQLModel, Field as SQLField, Session, create_engine, Relationship, or_, select, col

# =========================================================================
# 🗄️ DATENBANK-MODELLIERUNG (SQLModel & SQLite)
# =========================================================================

class NoteTag(SQLModel, table=True):
    # Verknuepft Notizen und Tags miteinander (n:m Beziehung)
    __tablename__ = "note_tag"
    note_id: Optional[int] = SQLField(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = SQLField(default=None, foreign_key="tags.id", primary_key=True)


class Note(SQLModel, table=True):
    # Repraesentiert eine Notiz in der Datenbank
    __tablename__ = 'notes'
    id: Optional[int] = SQLField(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = SQLField(default_factory=datetime.now)
    
    # Eine Notiz kann mehrere Tags haben
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTag)


class Tag(SQLModel, table=True):
    # Repraesentiert einen Tag in der Datenbank
    __tablename__ = 'tags'
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str = SQLField(unique=True, index=True)
    
    # Ein Tag kann mit mehreren Notizen verknuepft sein
    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTag)


# Datenbankverbindung herstellen und Tabellen generieren
engine = create_engine("sqlite:///notes.db", connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)

# =========================================================================
# ⚙️ HILFSFUNKTIONEN & VALIDATOREN
# =========================================================================

def validate_and_normalize_tag(tag_name: str) -> str:
    # Validiert den Tag-Namen und bereinigt ihn (Whitespace, Kleinschreibung, Regex)
    if not isinstance(tag_name, str):
        raise ValueError("tag name must be a string")
    
    tag_name = tag_name.strip().lower()
    
    if len(tag_name) < 2:
        raise ValueError("tag name must be at least 2 characters")
    if len(tag_name) > 30:
        raise ValueError("tag name must be at most 30 characters")
    if not re.match(r"^[a-z0-9-]+$", tag_name):
        raise ValueError("tag name must contain only lowercase letters, digits, and dashes")
        
    return tag_name


def get_session():
    # Erstellt fuer jeden Request eine neue Datenbank-Session
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


def parse_iso_datetime(value: Optional[str], param_name: str) -> Optional[datetime]:
    # Konvertiert einen ISO-Datumsstring in ein Python-datetime-Objekt
    if value is None:
        return None
    try:
        clean_value = value.replace("Z", "")
        return datetime.fromisoformat(clean_value)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail={"loc": ["query", param_name], "msg": "Invalid datetime format. Use ISO 8601.", "type": "value_error"},
        )

# =========================================================================
# 📋 PYDANTIC API-SCHEMATA (Eingabe / Ausgabe)
# =========================================================================

class NoteCreate(BaseModel):
    # Schema fuer das Erstellen einer neuen Notiz
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1, max_length=10000)
    category: str = Field(min_length=2, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=10)
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
    
    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        # Validiert und dedupliziert die uebergebenen Tags
        if not isinstance(v, list):
            raise ValueError("tags must be a list")
        
        validated_tags = []
        seen = set()
        
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("each tag must be a string")
            try:
                tag_normalized = validate_and_normalize_tag(tag)
                if tag_normalized not in seen:
                    validated_tags.append(tag_normalized)
                    seen.add(tag_normalized)
            except ValueError as e:
                raise ValueError(f"Invalid tag '{tag}': {str(e)}")
                
        return validated_tags


class NoteUpdate(BaseModel):
    # Schema fuer die partielle Aktualisierung (PATCH) einer Notiz
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    category: Optional[str] = Field(None, min_length=2, max_length=30)
    tags: Optional[list[str]] = Field(None, max_length=10)
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
    
    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        # Validiert die Tags fuer das Update-Schema, falls vorhanden
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("tags must be a list")
            
        validated_tags = []
        seen = set()
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("each tag must be a string")
            try:
                tag_normalized = validate_and_normalize_tag(tag)
                if tag_normalized not in seen:
                    validated_tags.append(tag_normalized)
                    seen.add(tag_normalized)
            except ValueError as e:
                raise ValueError(f"Invalid tag '{tag}': {str(e)}")
        return validated_tags
        
    @model_validator(mode="after")
    def validate_work_category_requires_work_tag(self):
        # Cross-Field-Validation: 'work'-Kategorie erfordert zwingend den 'work'-Tag
        if self.category == "work" and self.tags is not None and "work" not in self.tags:
            raise ValueError("work notes must include the 'work' tag")
        return self


class NoteResponse(BaseModel):
    # Schema fuer die API-Antworten
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)

# =========================================================================
# 🚀 FASTAPI ANWENDUNG & ENDPUNKTE
# =========================================================================

app = FastAPI(
    title="Note Taking API",
    description="Einfache, hochgradig validierte Notizenverwaltung mit SQLite-Backend",
    version="1.0.0"
)

# --- BASIS ROUTEN (Tag 1) ---

@app.get("/")
def root():
    # Einfacher Hello-World-Willkommensendpunkt
    return {"message": "Hello, World!"}

@app.get("/name/{name}")
def greet_name(name: str):
    # Gibt den uebergebenen Namen im JSON-Format zurueck
    return {"message": f"Hello, {name}!"}

@app.get("/calculate/{number}")
def calculate(number: float):
    # Fuehrt eine einfache mathematische Berechnung aus
    result = number * 2 + 5
    return {"message": f"Der verrechnete Wert von {number} ist {result}"}


# --- CRUD OPERATIONEN (Tag 2 & Tag 3) ---

@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    # Erstellt eine neue Notiz in der Datenbank und verknuepft Tags
    db_note = Note(title=note.title, content=note.content, category=note.category)
    
    tag_objects = []
    for tag_name in note.tags:
        statement = select(Tag).where(Tag.name == tag_name)
        existing_tag = session.exec(statement).first()
        
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name)
            session.add(new_tag)
            tag_objects.append(new_tag)
            
    db_note.tags = tag_objects
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], created_at=db_note.created_at.isoformat()
    )


@app.get("/notes")
def list_notes(
    session: SessionDep,
    category: Optional[str] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
) -> list[NoteResponse]:
    # Gibt alle Notizen aus. Filter fuer Kategorie, Suche, Tags und Datum sind optional kombinierbar.
    statement = select(Note)
    
    if category:
        statement = statement.where(Note.category == category)
    
    if search:
        search_lower = search.lower()
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{search_lower}%"),
                col(Note.content).ilike(f"%{search_lower}%")
            )
        )
    
    if tag:
        tag_lower = tag.lower()
        statement = statement.join(Note.tags).where(Tag.name == tag_lower)

    if created_after:
        created_after_dt = parse_iso_datetime(created_after, "created_after")
        statement = statement.where(Note.created_at >= created_after_dt)

    if created_before:
        created_before_dt = parse_iso_datetime(created_before, "created_before")
        statement = statement.where(Note.created_at <= created_before_dt)
    
    notes = session.exec(statement).all()
    
    return [
        NoteResponse(
            id=n.id, title=n.title, content=n.content, category=n.category,
            tags=[t.name for t in n.tags], created_at=n.created_at.isoformat()
        ) for n in notes
    ]


@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    # Ruft eine spezifische Notiz anhand ihrer ID ab
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(
        id=note.id, title=note.title, content=note.content, category=note.category,
        tags=[t.name for t in note.tags], created_at=note.created_at.isoformat()
    )


@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    # Aktualisiert eine vorhandene Notiz vollstaendig (PUT)
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = note_update.title
    note.content = note_update.content
    note.category = note_update.category

    tag_objects = []
    for tag_name in note_update.tags:
        stmt = select(Tag).where(Tag.name == tag_name)
        existing = session.exec(stmt).first()
        if existing:
            tag_objects.append(existing)
        else:
            new_tag = Tag(name=tag_name)
            session.add(new_tag)
            tag_objects.append(new_tag)

    note.tags = tag_objects
    session.add(note)
    session.commit()
    session.refresh(note)
    
    return NoteResponse(
        id=note.id, title=note.title, content=note.content, category=note.category,
        tags=[t.name for t in note.tags], created_at=note.created_at.isoformat()
    )


@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate, session: SessionDep) -> NoteResponse:
    # Aktualisiert eine Notiz teilweise (PATCH)
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = note_update.model_dump(exclude_unset=True)

    if "tags" in update_data:
        tag_objects = []
        for tag_name in update_data["tags"]:
            stmt = select(Tag).where(Tag.name == tag_name)
            existing = session.exec(stmt).first()
            if existing:
                tag_objects.append(existing)
            else:
                new_tag = Tag(name=tag_name)
                session.add(new_tag)
                tag_objects.append(new_tag)
        note.tags = tag_objects

    for key, value in update_data.items():
        if key == "tags":
            continue
        setattr(note, key, value)

    session.add(note)
    session.commit()
    session.refresh(note)

    return NoteResponse(
        id=note.id, title=note.title, content=note.content, category=note.category,
        tags=[t.name for t in note.tags], created_at=note.created_at.isoformat()
    )


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    # Loescht eine Notiz permanent aus der Datenbank
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return Response(status_code=204)


# --- META & STATISTIK ENDPUNKTE ---

@app.get("/notes/stats")
def get_notes_stats(session: SessionDep):
    # Berechnet globale Metadaten (Gesamtanzahl, Kategorien-Verteilung, Top 5 Tags)
    notes = session.exec(select(Note)).all()

    categories: dict[str, int] = {}
    tag_counts: dict[str, int] = {}

    for note in notes:
        categories[note.category] = categories.get(note.category, 0) + 1
        for tag in note.tags:
            tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1

    top_tags = [
        {"tag": tag, "count": count}
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    ][:5]

    unique_tags_count = len(session.exec(select(Tag)).all())

    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": top_tags,
        "unique_tags_count": unique_tags_count
    }


@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    # Listet alle verfuegbaren Tags alphabetisch sortiert auf
    tags = session.exec(select(Tag)).all()
    return sorted([tag.name for tag in tags])


@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    # Gibt alle Notizen zurueck, die einen bestimmten Tag besitzen
    tag_lower = tag_name.lower()
    tag = session.exec(select(Tag).where(Tag.name == tag_lower)).first()
    
    if not tag:
        return []
    
    return [
        NoteResponse(
            id=note.id, title=note.title, content=note.content, category=note.category,
            tags=[t.name for t in note.tags], created_at=note.created_at.isoformat()
        ) for note in tag.notes
    ]


@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    # Listet alle aktuell verwendeten Kategorien ohne Duplikate auf
    categories = session.exec(select(Note.category).distinct()).all()
    return sorted(categories)


@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str, session: SessionDep) -> list[NoteResponse]:
    # Gibt alle Notizen einer bestimmten Kategorie zurueck
    notes = session.exec(select(Note).where(Note.category == category_name)).all()
    return [
        NoteResponse(
            id=note.id, title=note.title, content=note.content, category=note.category,
            tags=[t.name for t in note.tags], created_at=note.created_at.isoformat()
        ) for note in notes
    ]
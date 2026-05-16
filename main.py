from fastapi import FastAPI, HTTPException, Response, Depends
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict, EmailStr
from datetime import datetime
import re
from typing import Optional, Annotated
from collections import Counter
from sqlmodel import SQLModel, Field as SQLField, Session, create_engine, Relationship, or_, select, col

# =========================================================================
# 🗄️ DATENBANK-MODELLIERUNG (SQLModel & SQLite)
# =========================================================================

class NoteTag(SQLModel, table=True):
    """
    Verknuepft Notizen und Tags miteinander (n:m Beziehung ueber eine Zwischentabelle).
    Anforderung aus Tag 3/4.
    """
    __tablename__ = "note_tag"
    note_id: Optional[int] = SQLField(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = SQLField(default=None, foreign_key="tags.id", primary_key=True)


class Note(SQLModel, table=True):
    """
    Repraesentiert eine Notiz in der persistenten SQLite-Datenbank.
    Enthaelt alle erweiterten Felder bis Tag 7 (priority, author_email).
    """
    __tablename__ = 'notes'
    id: Optional[int] = SQLField(default=None, primary_key=True)
    title: str
    content: str
    category: str
    priority: int = SQLField(default=3)  # Prioritaet von 1 bis 5 (Tag 5 Stretch Goal)
    author_email: Optional[str] = SQLField(default=None)  # E-Mail-Adresse des Autors (Tag 5 Stretch Goal)
    created_at: datetime = SQLField(default_factory=datetime.now)
    
    # Beziehung zu den Tags mit automatischer Verknuepfung
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTag)


class Tag(SQLModel, table=True):
    """
    Repraesentiert einen dynamischen Tag in der Datenbank.
    """
    __tablename__ = 'tags'
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str = SQLField(unique=True, index=True)
    
    # Inverse Beziehung zu den Notizen
    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTag)


# Erstellung der lokalen SQLite-Datenbankdatei (notes.db)
engine = create_engine("sqlite:///notes.db", connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)

# =========================================================================
# ⚙️ HILFSFUNKTIONEN & VALIDATOREN
# =========================================================================

def validate_and_normalize_tag(tag_name: str) -> str:
    """
    Validiert und normalisiert Tag-Namen nach den strikten Vorgaben aus Tag 5:
    - Nur Kleinbuchstaben, Zahlen und Bindestriche erlaubt
    - Laenge zwischen 2 und 30 Zeichen
    """
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
    """
    Erstellt eine isolierte Datenbank-Session fuer jeden eingehenden HTTP-Request.
    """
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


def parse_iso_datetime(value: Optional[str], param_name: str) -> Optional[datetime]:
    """
    Konvertiert ISO 8601 Datumsstrings fuer die Filter-Endpunkte robust in datetime-Objekte.
    """
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
# 📋 PYDANTIC API-SCHEMATA (Strikte Validierung nach Tag 5)
# =========================================================================

class NoteCreate(BaseModel):
    """
    Schema fuer die Validierung von POST- und PUT-Requests.
    Verhindert unangekuendigte Felder via extra='forbid' (Anforderung Tag 5).
    """
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=1, max_length=10000)
    category: str = Field(min_length=2, max_length=30)
    priority: int = Field(default=3, ge=1, le=5)  # Validierung: Bereich 1-5
    author_email: Optional[EmailStr] = Field(default=None)  # Automatische E-Mail-Validierung
    tags: list[str] = Field(default_factory=list, max_length=10)
    
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatische Bereinigung von Leerzeichen
        extra="forbid"              # Striktes Ablehnen unbekannter JSON-Felder
    )
    
    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
        """
        Dedupliziert und bereinigt eingehende Tags vor der Speicherung (Tag 5).
        """
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

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        """
        Normalisiert die Kategorie automatisch in Kleinschreibung (Tag 5).
        """
        return v.strip().lower()


class NoteUpdate(BaseModel):
    """
    Schema fuer partielle Aktualisierungen (PATCH-Requests).
    Alle Felder sind optional.
    """
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    category: Optional[str] = Field(None, min_length=2, max_length=30)
    priority: Optional[int] = Field(None, ge=1, le=5)
    author_email: Optional[EmailStr] = Field(None)
    tags: Optional[list[str]] = Field(None, max_length=10)
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
    
    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v):
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

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return v.strip().lower()
        
    @model_validator(mode="after")
    def validate_work_category_requires_work_tag(self):
        """
        Cross-Field-Validation: Falls Kategorie 'work' ist, muss auch das Tag 'work' existieren.
        """
        if self.category == "work" and self.tags is not None and "work" not in self.tags:
            raise ValueError("work notes must include the 'work' tag")
        return self


class NoteResponse(BaseModel):
    """
    Einheitliches API-Ausgabe-Schema. Garantiert saubere JSON-Strukturen im Frontend.
    """
    id: int
    title: str
    content: str
    category: str
    priority: int
    author_email: Optional[str]
    tags: list[str]
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)

# =========================================================================
# 🚀 FASTAPI ANWENDUNG & ENDPUNKTE
# =========================================================================

app = FastAPI(
    title="Ilia Beliaev - University API",
    description="Zentrales Repository fuer Applied Programming. Absolut sicher mit Pydantic v2 & SQLite SQLModel Backend.",
    version="7.0.0"
)

# --- BASISROUTEN & MATHEMATISCHE BERECHNUNGEN (Tag 1) ---

@app.get("/")
def read_root():
    return {"message": "Hello World!"}


@app.get("/status")
def get_status():
    return {"status": "online", "version": "7.0.0", "day": 7}


@app.get("/about")
def get_about():
    return {"project": "University API", "author": "Ilia Beliaev", "course": "Applied Programming"}


@app.get("/student")
def get_student():
    """
    Gibt die Profildaten des Studierenden aus (Anforderung Tag 1 / Klausurrelevat).
    """
    return {"name": "Ilia Beliaev", "course": "Applied Programming", "university": "TH Coburg"}


@app.get("/square/{number}")
def calculate_square(number: int):
    return {"number": number, "square": number * number}


@app.get("/double/{number}")
def calculate_double(number: int):
    return {"number": number, "double": number * 2}


# --- REST CRUD OPERATIONEN FÜR NOTIZEN (Tag 2, 3, 4) ---

@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    """
    Erstellt eine neue Notiz. Verknuepft oder generiert dabei dynamisch Tags.
    """
    db_note = Note(
        title=note.title, content=note.content, category=note.category,
        priority=note.priority, author_email=note.author_email
    )
    
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
        priority=db_note.priority, author_email=db_note.author_email,
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
    """
    Listet Notizen auf. Unterstuetzt kombinierbare Filter fuer Kategorie, Tags, Volltextsuche und Erstellungszeitraum.
    """
    statement = select(Note)
    
    if category:
        statement = statement.where(Note.category == category.lower())
    
    if search:
        search_lower = search.lower()
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{search_lower}%"),
                col(Note.content).ilike(f"%{search_lower}%")
            )
        )
    
    if tag:
        statement = statement.join(Note.tags).where(Tag.name == tag.lower())

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
            priority=n.priority, author_email=n.author_email,
            tags=[t.name for t in n.tags], created_at=n.created_at.isoformat()
        ) for n in notes
    ]


@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(
        id=note.id, title=note.title, content=note.content, category=note.category,
        priority=note.priority, author_email=note.author_email,
        tags=[t.name for t in note.tags], created_at=note.created_at.isoformat()
    )


@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    """
    Vollstaendiges Ueberschreiben einer bestehenden Notiz (PUT).
    """
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = note_update.title
    note.content = note_update.content
    note.category = note_update.category
    note.priority = note_update.priority
    note.author_email = note_update.author_email

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
        priority=note.priority, author_email=note.author_email,
        tags=[t.name for t in note.tags], created_at=note.created_at.isoformat()
    )


@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate, session: SessionDep) -> NoteResponse:
    """
    Teilweises Aktualisieren einer Notiz (PATCH). Unveraenderte Felder werden beibehalten.
    """
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
        priority=note.priority, author_email=note.author_email,
        tags=[t.name for t in note.tags], created_at=note.created_at.isoformat()
    )


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return Response(status_code=204)


# --- STATISTIKEN & META-ENDPUNKTE (Tag 3, 5) ---

@app.get("/notes/stats")
def get_notes_stats(session: SessionDep):
    """
    Aggregiert globale Statistiken fuer das Streamlit-Dashboard (Gesamtanzahl, Kategorien, Top 5 Tags).
    """
    notes = session.exec(select(Note)).all()
    categories = {}
    all_tags_list = []
    
    for n in notes:
        categories[n.category] = categories.get(n.category, 0) + 1
        for t in n.tags:
            all_tags_list.append(t.name)
            
    tag_counts = Counter(all_tags_list)
    unique_tags_count = len(session.exec(select(Tag)).all())

    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": [{"tag": tag, "count": count} for tag, count in tag_counts.most_common(5)],
        "unique_tags_count": unique_tags_count
    }


@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    tags = session.exec(select(Tag)).all()
    return sorted([tag.name for tag in tags])


@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    categories = session.exec(select(Note.category).distinct()).all()
    return sorted(categories)
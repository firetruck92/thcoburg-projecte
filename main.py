from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict, EmailStr
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Optional, Annotated
from collections import Counter
from sqlmodel import SQLModel, Field as SQLField, Session, create_engine, Relationship, select, or_, col

# =========================================================================
# 🚀 INITIALIZATION & CONFIGURATION
# =========================================================================

app = FastAPI(
    title="Ilia Beliaev - University API",
    description="Central repository for all course days. Bulletproof with Pydantic v2 & SQLite SQLModel Backend.",
    version="7.0.0"
)

# =========================================================================
# 📅 TAG 1: BASIC ENDPOINTS & MATHEMATICAL CALCULATIONS
# =========================================================================

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/status")
def get_status():
    return {"status": "online", "version": "7.0.0", "day": 7}

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
# 📝 TAG 2: NOTE API WITH PERSISTENT JSON STORAGE (LEGACY)
# =========================================================================

NOTES_FILE = Path("data/notes.json")

class NoteCreateV2(BaseModel):
    title: str
    content: str
    category: str

class NoteV2(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: str

def load_notes_v2():
    notes_db = []
    note_id_counter = 1
    if NOTES_FILE.exists():
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                notes_db = [NoteV2(**note) for note in data]
                if notes_db:
                    note_id_counter = max(note.id for note in notes_db) + 1
            except json.JSONDecodeError:
                pass
    return notes_db, note_id_counter

def save_notes_v2(notes_db):
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        notes_data = [note.model_dump() for note in notes_db]
        json.dump(notes_data, f, indent=2, ensure_ascii=False)

@app.post("/v2/notes", status_code=201)
def create_note_v2(note: NoteCreateV2) -> NoteV2:
    notes_db, note_id_counter = load_notes_v2()
    new_note = NoteV2(
        id=note_id_counter, title=note.title, content=note.content,
        category=note.category, created_at=datetime.now(timezone.utc).isoformat()
    )
    notes_db.append(new_note)
    save_notes_v2(notes_db)
    return new_note


# =========================================================================
# 🗄️ TAG 3: SQLMODEL DATABASE TABLES (SQLITE BACKEND)
# =========================================================================

DATABASE_URL = "sqlite:///notes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

class NoteTagLink(SQLModel, table=True):
    __tablename__ = "notetaglink"
    note_id: Optional[int] = SQLField(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = SQLField(default=None, foreign_key="tags.id", primary_key=True)

class Note(SQLModel, table=True):
    __tablename__ = "notes"
    id: Optional[int] = SQLField(default=None, primary_key=True)
    title: str
    content: str
    category: str
    author_email: Optional[str] = SQLField(default=None)  # Tag 5 Stretch Goal
    priority: int = SQLField(default=3)                  # Tag 5 Stretch Goal
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(timezone.utc))
    tags: list["Tag"] = Relationship(back_populates="notes", link_model=NoteTagLink)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str = SQLField(unique=True, index=True)
    notes: list[Note] = Relationship(back_populates="tags", link_model=NoteTagLink)

SQLModel.metadata.create_all(engine)


# =========================================================================
# 📋 TAG 4 & 5: PYDANTIC VALIDATION MODELS (CORE HARDENING)
# =========================================================================

class NoteCreate(BaseModel):
    # Auto-strip whitespace and forbid unknown extra fields (Tag 5 Core)
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    
    # Validation constraints from Tag 4
    title: str = Field(..., min_length=3, max_length=50)
    content: str = Field(..., min_length=5)
    category: str = Field(..., min_length=2, max_length=20)
    tags: list[str] = []
    author_email: Optional[EmailStr] = None  # Tag 5 Stretch Goal
    priority: int = Field(default=3, ge=1, le=5)  # Tag 5 Stretch Goal

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        """Enforce lowercase for categories (Tag 5 Rule)"""
        return v.lower()

    @field_validator("tags")
    @classmethod
    def clean_and_deduplicate_tags(cls, v: list[str]) -> list[str]:
        """Deduplicate tags case-insensitively (Tag 5 Rule)"""
        cleaned = []
        seen = set()
        for tag in v:
            t_clean = tag.strip().lower()
            if t_clean and t_clean not in seen:
                seen.add(t_clean)
                cleaned.append(t_clean)
        return cleaned

    @model_validator(mode="after")
    def check_title_and_content_distinct(self) -> "NoteCreate":
        """Cross-field validation: Title and content must be different (Tag 5 Rule)"""
        if self.title.lower() == self.content.lower():
            raise ValueError("Title and content must be distinctly different!")
        return self


class NoteUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    content: Optional[str] = Field(None, min_length=5)
    category: Optional[str] = Field(None, min_length=2, max_length=20)
    tags: Optional[list[str]] = None
    author_email: Optional[EmailStr] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: Optional[str]) -> Optional[str]:
        return v.lower() if v is not None else None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    author_email: Optional[str] = None
    priority: int
    created_at: str

    class Config:
        from_attributes = True


# =========================================================================
# 🛣️ API ENDPOINTS (DATABASE CRUD - TAG 3, 4, 5, 6)
# =========================================================================

def get_or_create_tags(tag_names: list[str], session: SessionDep) -> list[Tag]:
    tag_objects = []
    for name in tag_names:
        statement = select(Tag).where(Tag.name == name)
        existing_tag = session.exec(statement).first()
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=name)
            session.add(new_tag)
            tag_objects.append(new_tag)
    return tag_objects

@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    db_note = Note(
        title=note.title, content=note.content, category=note.category,
        author_email=note.author_email, priority=note.priority
    )
    db_note.tags = get_or_create_tags(note.tags, session)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], author_email=db_note.author_email,
        priority=db_note.priority, created_at=db_note.created_at.isoformat()
    )

@app.get("/notes")
def list_notes(
    session: SessionDep, category: str = None, search: str = None, tag: str = None,
    created_after: str = None, created_before: str = None
) -> list[NoteResponse]:
    statement = select(Note)
    if category:
        statement = statement.where(Note.category == category.lower())
    if search:
        search_lower = search.lower()
        statement = statement.where(or_(col(Note.title).ilike(f"%{search_lower}%"), col(Note.content).ilike(f"%{search_lower}%")))
    if tag:
        statement = statement.join(Note.tags).where(Tag.name == tag.lower())
        
    notes = session.exec(statement).all()
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
            tags=[t.name for t in n.tags], author_email=n.author_email,
            priority=n.priority, created_at=n.created_at.isoformat()
        ) for n in filtered_notes
    ]

@app.get("/notes/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteResponse:
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], author_email=db_note.author_email,
        priority=db_note.priority, created_at=db_note.created_at.isoformat()
    )

@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
    db_note.title = note_update.title
    db_note.content = note_update.content
    db_note.category = note_update.category
    db_note.author_email = note_update.author_email
    db_note.priority = note_update.priority
    db_note.tags = get_or_create_tags(note_update.tags, session)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], author_email=db_note.author_email,
        priority=db_note.priority, created_at=db_note.created_at.isoformat()
    )

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
    if note_patch.author_email is not None:
        db_note.author_email = note_patch.author_email
    if note_patch.priority is not None:
        db_note.priority = note_patch.priority
    if note_patch.tags is not None:
        db_note.tags = get_or_create_tags(note_patch.tags, session)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return NoteResponse(
        id=db_note.id, title=db_note.title, content=db_note.content, category=db_note.category,
        tags=[t.name for t in db_note.tags], author_email=db_note.author_email,
        priority=db_note.priority, created_at=db_note.created_at.isoformat()
    )

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep):
    db_note = session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
    session.delete(db_note)
    session.commit()
    return

@app.get("/notes/stats")
def get_notes_stats(session: SessionDep):
    notes = session.exec(select(Note)).all()
    categories = {}
    all_tags_list = []
    for n in notes:
        categories[n.category] = categories.get(n.category, 0) + 1
        for t in n.tags:
            all_tags_list.append(t.name)
    tag_counts = Counter(all_tags_list)
    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": [{"tag": tag, "count": count} for tag, count in tag_counts.most_common(5)],
        "unique_tags_count": len(tag_counts)
    }

@app.get("/tags")
def list_tags(session: SessionDep) -> list[str]:
    tags = session.exec(select(Tag)).all()
    return sorted([t.name for t in tags])

@app.get("/categories")
def list_categories(session: SessionDep) -> list[str]:
    notes = session.exec(select(Note)).all()
    return sorted(list({n.category for n in notes}))
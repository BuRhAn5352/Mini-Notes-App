from typing import Annotated,Optional

from pydantic import BaseModel, Field, ConfigDict
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from sqlalchemy import select

from db import get_db, Note


app = FastAPI()

#---------- REQUEST SCHEMAS-------

class NotesCreate(BaseModel):
    id: Annotated[int ,  Field(...,description="enter your id")]
    title: Annotated[str, Field(...,description="enter title of your note")]
    content: Annotated[str,Field(...,description="Write your Content")] | None=None

class Notes_Update(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# ------RESPONSE SCHEMAS ------ 

class NoteResponse(BaseModel):
    id : int
    title : str
    content : str | None = None

    model_config = ConfigDict(from_attributes=True)

#----------- DATABASE DEPENDENCY ---------
DbSession = Annotated[Session, Depends(get_db)]

#-- ROUTES ---
# HOME

@app.get("/")
def hello():
    return {"message":"Welcome to Mini Notes Web Page, Write your notes here hon :)"}


# CREATENOTE 

@app.post(
        "/notes",
        response_model=NoteResponse,
        status_code=status.HTTP_201_CREATED
        )
def create_notes(
    notes : NotesCreate,
    session : DbSession
    ):
    note = Note(
    id=notes.id,
    title=notes.title,
    content=notes.content
)
    session.add(note)
    session.commit()
    session.refresh(note)

    return note

# get a single note

@app.get("/notes/{notes_id}",
         response_model=NoteResponse
    )
def get_note(
    notes_id : int,
    session : DbSession
    ):

    note = session.get(Note,notes_id)

    if note is None:
        raise HTTPException(404,detail="doesn't exist")

    return note


# Update Note


@app.patch('/edit/{notes_id}')
def edit_notes(
    notes_id : int,
    notes_update : Notes_Update,
    session : DbSession
):
    note = session.get(Note,notes_id)

    if note is None:
        raise  HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Note doesn't exists")

    update_data = notes_update.model_dump(exclude_unset=True)

    if "title" in update_data and update_data["title"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title cannnot be null"
        )

    for field, value in update_data.items():
        setattr(note,field,value)

    session.commit()
    session.refresh(note)

    return {"message": "the note has been updated",
            "note": note
            }

#--DELETE_NOTE---

@app.delete('/notes/{notes_id}')
def delete_note(
        notes_id: int,
        session: DbSession
):
    note=session.get(Note,notes_id)

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Note ID - Note doesn't exists")

    session.delete(note)
    session.commit()

    return {
        "message":"the note has been deleted"
        }

# GET ALL THE NOTES

@app.get('/notes',response_model=list[NoteResponse])
def get_notes(
    session : DbSession
):
    stmt = select(Note)
    result = session.execute(stmt)
    notes = result.scalars(stmt).all()

    return notes

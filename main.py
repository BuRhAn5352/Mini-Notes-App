from typing import Annotated,Optional

from pydantic import BaseModel, Field, ConfigDict
from fastapi import FastAPI, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from sqlalchemy import select, func 

from db import get_db, Note, User
from schemas import UserCreate, UserResponse
from security import hash_password

from security import verify_password,create_access_token


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


class NotesListResponse(BaseModel):
    total : int 
    page : int 
    limit : int 
    total_pages : int 
    has_next : bool
    has_previous : bool 
    notes : list[NoteResponse]

#----------- DATABASE DEPENDENCY ---------
DbSession = Annotated[Session, Depends(get_db)]

#-- ROUTES ---
# HOME

@app.post("/register",
        response_model = UserResponse,
        status_code=status.HTTP_201_CREATED
        )

def register_user(
    user_data:UserCreate,
    session : DbSession
):
    existing_user = session.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail= "Email already registered"
        )

    hashed_password= hash_password(user_data.password)

    new_user= User(
        email=user_data.email,
        hashed_password = hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@app.post("/login")
def login(
    user_data : UserCreate,
    session : DbSession
):
    user = session.scalar(
        select(Note).where(User.email == user_data.email)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user_data.password,user.hashed_password):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)
    
    return {
        "access_token": access_token,
        "token_type" : " bearer"
    }


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

@app.get('/notes',response_model=NotesListResponse)
def get_notes(
    session: DbSession,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge= 1, le=100),
    search: str | None=None,
    has_content: bool | None = None
):

    #pagination 
    offset = (page-1) * limit

    #buid the main db query
    stmt = select(Note)

    if search :
        stmt = select(Note).where(Note.title.ilike(f"%{search}%"))

    if has_content is True:
        stmt=select(Note).where(
            Note.content.is_not(None) & (Note.content != "")
            )

    elif has_content is False:
        stmt=select(Note).where(
            Note.content.is_(None) | (Note.content == "")
            )
    
    
    # count matching notes
    count_notes = select(func.count()).select_from(Note)

    if search: 
        count_notes= count_notes.where(Note.title.ilike(f"%{search}%"))


    if has_content is True:
        count_notes= count_notes.where(
            Note.content.is_not(None) & (Note.content != "")
            )

    elif has_content is False:
        count_notes  = count_notes.where(
            Note.content.is_(None) | (Note.content=="")
        )

    total = session.scalar(count_notes)

    #pagination metadata
    total_pages = (total + limit -1 ) // limit


    has_next = page < total_pages
    has_previous = page > 1


    # fetchng notes
    stmt = select(Note).order_by(Note.id.asc()).offset(offset).limit(limit)

    result = session.execute(stmt)
    notes = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_previous": has_previous,
        "notes" : notes
    }

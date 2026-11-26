from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Annotated,Optional


class UserCreate(BaseModel):
    email : EmailStr
    password : str

class UserResponse(BaseModel):
    id : int
    email : EmailStr

    model_config= {"from_attributes": True}


class NotesCreate(BaseModel):
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

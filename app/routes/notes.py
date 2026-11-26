from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Note, User
from app.schemas import (
    NotesCreate,
    Notes_Update,
    NoteResponse,
    NotesListResponse
)
from app.routes.auth import get_current_user
from app.logging_config import logger


router = APIRouter(tags=["Notes"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED
)
def create_notes(
    notes: NotesCreate,
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_user)]
):
    new_note = Note(
        title=notes.title,
        content=notes.content,
        user_id=current_user.id
    )

    session.add(new_note)
    session.commit()

    logger.info(
        "Note created: user_id=%s note_id=%s",
        current_user.id,
        new_note.id
    )

    session.refresh(new_note)

    return new_note


@router.get(
    "/notes/{notes_id}",
    response_model=NoteResponse
)
def get_note(
    notes_id: int,
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_user)]
):
    note = session.scalar(
        select(Note).where(
            Note.id == notes_id,
            Note.user_id == current_user.id
        )
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note doesn't exist"
        )

    logger.debug(
        "Note retrieved: user_id=%s note_id=%s",
        current_user.id,
        note.id
    )

    return note


@router.patch("/edit/{notes_id}")
def edit_notes(
    notes_id: int,
    notes_update: Notes_Update,
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_user)]
):
    note = session.scalar(
        select(Note).where(
            Note.id == notes_id,
            Note.user_id == current_user.id
        )
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note doesn't exist"
        )

    update_data = notes_update.model_dump(exclude_unset=True)

    if "title" in update_data and update_data["title"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title cannot be null"
        )

    for field, value in update_data.items():
        setattr(note, field, value)

    session.commit()

    logger.info(
        "Note updated: user_id=%s note_id=%s",
        current_user.id,
        note.id
    )

    session.refresh(note)

    return {
        "message": "The note has been updated",
        "note": note
    }


@router.delete("/notes/{notes_id}")
def delete_note(
    notes_id: int,
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_user)]
):
    note = session.scalar(
        select(Note).where(
            Note.id == notes_id,
            Note.user_id == current_user.id
        )
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note doesn't exist"
        )

    session.delete(note)
    session.commit()

    logger.info(
        "Note deleted: user_id=%s note_id=%s",
        current_user.id,
        note.id
    )

    return {"message": "The note has been deleted"}


@router.get("/notes", response_model=NotesListResponse)
def get_notes(
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    has_content: bool | None = None
):
    offset = (page - 1) * limit

    stmt = select(Note).where(
        Note.user_id == current_user.id
    )

    count_notes = (
        select(func.count())
        .select_from(Note)
        .where(Note.user_id == current_user.id)
    )

    if search:
        condition = Note.title.ilike(f"%{search}%")
        stmt = stmt.where(condition)
        count_notes = count_notes.where(condition)

    if has_content is True:
        condition = (
            Note.content.is_not(None) &
            (Note.content != "")
        )
        stmt = stmt.where(condition)
        count_notes = count_notes.where(condition)

    elif has_content is False:
        condition = (
            Note.content.is_(None) |
            (Note.content == "")
        )
        stmt = stmt.where(condition)
        count_notes = count_notes.where(condition)

    total = session.scalar(count_notes) or 0

    total_pages = (total + limit - 1) // limit

    has_next = page < total_pages
    has_previous = page > 1

    stmt = (
        stmt.order_by(Note.id.asc())
        .offset(offset)
        .limit(limit)
    )

    notes = session.scalars(stmt).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_previous": has_previous,
        "notes": notes
    }
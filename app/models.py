from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

class Base(DeclarativeBase):
    pass

class Note(Base):
    __tablename__=  "notes_data"

    id : Mapped[int]= mapped_column(primary_key=True)
    title : Mapped[str]
    content: Mapped[str | None] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="notes")

class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    email : Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    notes: Mapped[list["Note"]] = relationship(back_populates="user")
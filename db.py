import os
from typing import Generator

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column, 
    Session, 
    sessionmaker,
    relationship,
)

from dotenv import load_dotenv




load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


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

engine = create_engine(DATABASE_URL)

SessionFactory=sessionmaker(engine)
""" 
# two Nones - one for returning if we send smthng back to the generator, we dont
 third none for type of value the generator returns when it finishes, here there is nothing like (return "database closed"),
 it simply ends so none
 
# Generator[YieldType, SendType, ReturnType]

"""
def get_db() -> Generator[Session,None,None]:
    session = SessionFactory()

    try:
        yield session
    finally:
        session.close()
    
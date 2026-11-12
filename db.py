import sqlalchemy as db
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from dotenv import load_dotenv
import os



class Base(DeclarativeBase):
    pass

class Note(Base):
    __tablename__=  "notes_data"

    id : Mapped[int]= mapped_column(primary_key=True)
    title : Mapped[str]
    content: Mapped[str]


load_dotenv()

Database_url=os.getenv("DATABASE_URL")

engine = create_engine(Database_url)
Base.metadata.create_all(engine)

sessionfactory=sessionmaker(engine)

def get_db():
    session=sessionfactory()
    try:
        yield session
    finally:
        session.close()
    

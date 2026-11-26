import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


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
    
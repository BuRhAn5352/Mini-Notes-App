from fastapi import FastAPI

from app.routes import auth, notes
from app.logging_config import logger

app = FastAPI(title="Mini Notes API")

app.include_router(auth.router)
app.include_router(notes.router)


@app.on_event("startup")
def startup_event():
    logger.info("Mini Notes API started")


@app.get("/")
def hello():
    return {
        "message": "Welcome to Mini Notes API"
    }
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import Base, engine, get_db
from app.routers import riddles

app = FastAPI(title="Nazo API", version="0.1.0")

app.include_router(riddles.router)

@app.get("/")
def root():
    return {"message": "Hello World from backend"}

@app.get("/health/db")
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
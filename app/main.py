from fastapi import FastAPI, Depends
from app.core.database import Base, engine, get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI(title="Nazo API", version="0.1.0")


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
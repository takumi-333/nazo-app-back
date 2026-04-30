from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routers import riddles, auth, health, dev

app = FastAPI(title="Nazo API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(riddles.router)
app.include_router(auth.router)

# for development
app.include_router(health.router)
app.include_router(dev.router)

@app.get("/")
def root():
    return {"message": "Hello World from backend"}


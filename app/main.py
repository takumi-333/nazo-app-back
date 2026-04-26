from fastapi import FastAPI

app = FastAPI(title="My API", version="0.1.0")


@app.get("/")
def root():
    return {"message": "Hello World from backend"}


@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}


@app.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"Hello, {name}!"}
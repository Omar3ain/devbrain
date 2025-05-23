from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import init_db
from app.routers import command, git

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(command.router)
app.include_router(git.router)

@app.get("/")
def read_root():
    return {"message": "DevBrain API is running"} 
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import aiosqlite
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_PATH = os.path.expanduser(os.getenv("DEVBRAIN_DB_PATH", "~/.devbrain/devbrain.db"))
DB_DIR = os.path.dirname(DB_PATH)
os.makedirs(DB_DIR, exist_ok=True)

app = FastAPI(title="DevBrain API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        yield db

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                output TEXT,
                timestamp DATETIME NOT NULL,
                directory TEXT NOT NULL,
                git_branch TEXT,
                tags TEXT
            )
        ''')
        await db.commit()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()

class Command(BaseModel):
    command: str
    output: Optional[str] = None
    timestamp: str
    directory: str
    git_branch: Optional[str] = None
    tags: Optional[List[str]] = []

@app.get("/")
async def root():
    return {"message": "Welcome to DevBrain API"}

@app.post("/commands")
async def log_command(command: Command, db: aiosqlite.Connection = Depends(get_db)):
    try:
        # Check if this exact command was run recently (within last 5 minutes)
        async with db.execute('''
            SELECT id FROM commands 
            WHERE command = ? 
            AND timestamp > datetime('now', '-5 minutes')
            LIMIT 1
        ''', (command.command,)) as cursor:
            if await cursor.fetchone():
                return {"status": "skipped", "message": "Command already logged recently"}

        # If not found, log the new command
        await db.execute('''
            INSERT INTO commands (command, timestamp, directory, git_branch, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            command.command,
            command.timestamp,
            command.directory,
            command.git_branch,
            ','.join(command.tags) if command.tags else None
        ))
        await db.commit()
        return {"status": "success", "message": "Command logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/commands/search")
async def search_commands(query: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        async with db.execute('''
            SELECT * FROM commands 
            WHERE command LIKE ? AND command NOT LIKE 'devbrain_search%'
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (f'%{query}%',)) as cursor:
            results = await cursor.fetchall()
            return {
                "status": "success",
                "results": [
                    {
                        "id": row[0],
                        "command": row[1],
                        "timestamp": row[3],
                        "directory": row[4],
                        "git_branch": row[5],
                        "tags": row[6].split(',') if row[6] else []
                    }
                    for row in results
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/git/changes")
async def get_git_changes(directory: str):
    try:
        with GitAnalyzer(directory) as analyzer:
            changes = analyzer.get_changes()
            return {
                "status": "success",
                "changes": [change for change in changes]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/git/commit-message")
async def generate_commit_message(directory: str):
    try:
        with GitAnalyzer(directory) as analyzer:
            return analyzer.generate_commit_message()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
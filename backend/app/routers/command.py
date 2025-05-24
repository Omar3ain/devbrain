from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import logging

from app.db.session import SessionLocal
from app.models.command import Command
from app.schemas.command import CommandCreate, Command as CommandSchema
from app.ai_tools.command_analyzer import CommandAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/commands",
    tags=["commands"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/natural-search")
def natural_search(query: str, db: Session = Depends(get_db)):
    try:
        analyzer = CommandAnalyzer()
        return analyzer.search_commands(query, db)
    except Exception as e:
        logger.error(f"Error in natural search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=CommandSchema)
def log_command(command: CommandCreate, db: Session = Depends(get_db)):
    try:
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_command = db.query(Command).filter(
            Command.command == command.command,
            Command.timestamp > five_minutes_ago
        ).first()
        
        if recent_command:
            return recent_command

        # Create new command
        db_command = Command(
            command=command.command,
            output=command.output,
            timestamp=command.timestamp if command.timestamp else datetime.utcnow(),
            directory=command.directory.rstrip(),
            git_branch=command.git_branch.rstrip(),
            tags=','.join(command.tags) if command.tags else None
        )
        
        db.add(db_command)
        db.commit()
        db.refresh(db_command)
        
        return db_command
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
def search_commands(query: str, db: Session = Depends(get_db)):
    try:
        logger.info(f"Searching for commands with query: {query}")
        commands = db.query(Command).filter(
            Command.command.like(f'%{query}%')
        ).order_by(Command.timestamp.desc()).all()
        
        logger.info(f"Found {len(commands)} commands")
        return {
            "status": "success",
            "results": [
                {
                    "id": cmd.id,
                    "command": cmd.command,
                    "timestamp": cmd.timestamp,
                    "directory": cmd.directory,
                    "git_branch": cmd.git_branch,
                    "tags": cmd.tags.split(',') if cmd.tags else []
                }
                for cmd in commands
            ]
        }
    except Exception as e:
        logger.error(f"Error searching commands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
    
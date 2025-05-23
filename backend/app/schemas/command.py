from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommandBase(BaseModel):
    command: str
    output: Optional[str] = None
    directory: str
    git_branch: Optional[str] = None
    tags: Optional[List[str]] = []

class CommandCreate(CommandBase):
    timestamp: Optional[datetime] = None

class Command(CommandBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True 
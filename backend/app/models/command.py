from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.session import Base

class Command(Base):
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, index=True)
    command = Column(String, nullable=False)
    output = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    directory = Column(String, nullable=False)
    git_branch = Column(String, nullable=True)
    tags = Column(String, nullable=True)

    def __repr__(self):
        return f"<Command(id={self.id}, command='{self.command}', timestamp='{self.timestamp}')>" 
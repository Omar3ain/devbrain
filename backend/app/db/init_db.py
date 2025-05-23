from app.db.session import engine, Base, init_db as session_init_db
from app.models.command import Command
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

if __name__ == "__main__":
    logger.info("Creating initial database tables...")
    init_db()
    logger.info("Database tables created.") 
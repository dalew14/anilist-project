from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Find the main project folder
BASE_DIR = Path(__file__).resolve().parents[2]

# Store the SQLite database in the data folder
DATABASE_URL = f"sqlite:///{(BASE_DIR / 'data' / 'anilist.db').as_posix()}"

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for our database models
Base = declarative_base()


# Provide a database session to API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
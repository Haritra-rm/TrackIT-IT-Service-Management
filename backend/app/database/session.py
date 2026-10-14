from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from app.database.connection import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator for FastAPI routes.
    Ensures that each HTTP request gets its own database session and closes it cleanly.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

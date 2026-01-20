"""SQLite database client using SQLAlchemy."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./messenger.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize the database by creating all tables."""
    from app.models.sqlite_models import User, Conversation, ConversationParticipant, Message
    Base.metadata.create_all(bind=engine)


def close_db() -> None:
    """Close database connections."""
    engine.dispose()

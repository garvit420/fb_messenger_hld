"""Test fixtures for the messaging application."""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.sqlite_client import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.sqlite_models import User, Conversation, ConversationParticipant, Message

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        password_hash=get_password_hash("testpassword123"),
        display_name="Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session: Session) -> User:
    """Create a second test user."""
    user = User(
        email="testuser2@example.com",
        username="testuser2",
        password_hash=get_password_hash("testpassword123"),
        display_name="Test User 2",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Create an auth token for the test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def auth_token2(test_user2: User) -> str:
    """Create an auth token for the second test user."""
    return create_access_token(data={"sub": str(test_user2.id)})


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def auth_headers2(auth_token2: str) -> dict:
    """Create authorization headers for second user."""
    return {"Authorization": f"Bearer {auth_token2}"}


@pytest.fixture
def test_conversation(db_session: Session, test_user: User, test_user2: User) -> Conversation:
    """Create a test conversation between two users."""
    conversation = Conversation()
    db_session.add(conversation)
    db_session.flush()

    participant1 = ConversationParticipant(conversation_id=conversation.id, user_id=test_user.id)
    participant2 = ConversationParticipant(conversation_id=conversation.id, user_id=test_user2.id)
    db_session.add(participant1)
    db_session.add(participant2)
    db_session.commit()
    db_session.refresh(conversation)

    return conversation


@pytest.fixture
def test_message(db_session: Session, test_conversation: Conversation, test_user: User) -> Message:
    """Create a test message."""
    message = Message(
        conversation_id=test_conversation.id,
        sender_id=test_user.id,
        content="Hello, this is a test message!",
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message

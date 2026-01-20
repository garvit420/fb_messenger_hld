"""Tests for conversation endpoints."""
import pytest
from fastapi.testclient import TestClient


class TestGetUserConversations:
    """Tests for getting user's conversations."""

    def test_get_conversations_success(
        self, client: TestClient, auth_headers, test_conversation, test_message
    ):
        """Test getting user's conversations."""
        response = client.get("/api/conversations/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["data"]) == 1
        conv = data["data"][0]
        assert conv["id"] == test_conversation.id
        assert "participants" in conv
        assert len(conv["participants"]) == 2

    def test_get_conversations_empty(
        self, client: TestClient, auth_headers, test_user
    ):
        """Test getting conversations when user has none."""
        response = client.get("/api/conversations/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["data"]) == 0

    def test_get_conversations_with_last_message(
        self, client: TestClient, auth_headers, test_conversation, test_message
    ):
        """Test that conversations include last message info."""
        response = client.get("/api/conversations/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        conv = data["data"][0]
        assert conv["last_message_content"] == test_message.content
        assert conv["last_message_at"] is not None

    def test_get_conversations_pagination(
        self, client: TestClient, auth_headers, db_session, test_user
    ):
        """Test conversation pagination."""
        from app.models.sqlite_models import Conversation, ConversationParticipant, User
        from app.core.security import get_password_hash

        # Create multiple conversations
        for i in range(15):
            # Create a new user for each conversation
            other_user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                password_hash=get_password_hash("password"),
                display_name=f"User {i}"
            )
            db_session.add(other_user)
            db_session.flush()

            conv = Conversation()
            db_session.add(conv)
            db_session.flush()

            p1 = ConversationParticipant(
                conversation_id=conv.id,
                user_id=test_user.id
            )
            p2 = ConversationParticipant(
                conversation_id=conv.id,
                user_id=other_user.id
            )
            db_session.add(p1)
            db_session.add(p2)

        db_session.commit()

        # Get first page
        response = client.get(
            "/api/conversations/?page=1&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["data"]) == 10
        assert data["page"] == 1

        # Get second page
        response = client.get(
            "/api/conversations/?page=2&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 5
        assert data["page"] == 2

    def test_get_conversations_unauthorized(self, client: TestClient):
        """Test getting conversations without auth fails."""
        response = client.get("/api/conversations/")
        assert response.status_code == 401


class TestGetConversation:
    """Tests for getting a specific conversation."""

    def test_get_conversation_success(
        self, client: TestClient, auth_headers, test_conversation, test_message
    ):
        """Test getting a specific conversation."""
        response = client.get(
            f"/api/conversations/{test_conversation.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_conversation.id
        assert "participants" in data
        assert len(data["participants"]) == 2
        assert data["last_message_content"] == test_message.content

    def test_get_conversation_participant_info(
        self, client: TestClient, auth_headers, test_conversation, test_user, test_user2
    ):
        """Test that conversation includes participant details."""
        response = client.get(
            f"/api/conversations/{test_conversation.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        participants = data["participants"]
        usernames = [p["username"] for p in participants]
        assert test_user.username in usernames
        assert test_user2.username in usernames

    def test_get_conversation_not_participant(
        self, client: TestClient, auth_headers, db_session
    ):
        """Test getting conversation when not a participant fails."""
        from app.models.sqlite_models import Conversation, ConversationParticipant, User
        from app.core.security import get_password_hash

        # Create two other users
        user_a = User(
            email="usera@example.com",
            username="usera",
            password_hash=get_password_hash("password")
        )
        user_b = User(
            email="userb@example.com",
            username="userb",
            password_hash=get_password_hash("password")
        )
        db_session.add(user_a)
        db_session.add(user_b)
        db_session.flush()

        # Create a conversation between them (not including test_user)
        conv = Conversation()
        db_session.add(conv)
        db_session.flush()

        p1 = ConversationParticipant(conversation_id=conv.id, user_id=user_a.id)
        p2 = ConversationParticipant(conversation_id=conv.id, user_id=user_b.id)
        db_session.add(p1)
        db_session.add(p2)
        db_session.commit()

        response = client.get(
            f"/api/conversations/{conv.id}",
            headers=auth_headers
        )
        assert response.status_code == 403
        assert "not a participant" in response.json()["detail"]

    def test_get_conversation_not_found(self, client: TestClient, auth_headers):
        """Test getting nonexistent conversation."""
        response = client.get(
            "/api/conversations/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == 403  # First check is participant check

    def test_get_conversation_unauthorized(
        self, client: TestClient, test_conversation
    ):
        """Test getting conversation without auth fails."""
        response = client.get(f"/api/conversations/{test_conversation.id}")
        assert response.status_code == 401

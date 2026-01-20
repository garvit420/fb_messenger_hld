"""Tests for message endpoints."""

from fastapi.testclient import TestClient


class TestSendMessage:
    """Tests for sending messages."""

    def test_send_message_new_conversation(
        self, client: TestClient, auth_headers, test_user, test_user2
    ):
        """Test sending a message creates a new conversation."""
        response = client.post(
            "/api/messages/",
            headers=auth_headers,
            json={"content": "Hello!", "receiver_id": test_user2.id},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello!"
        assert data["sender_id"] == test_user.id
        assert data["status"] == "sent"
        assert "conversation_id" in data
        assert "id" in data

    def test_send_message_existing_conversation(
        self, client: TestClient, auth_headers, test_user, test_conversation
    ):
        """Test sending a message to existing conversation."""
        response = client.post(
            "/api/messages/",
            headers=auth_headers,
            json={
                "content": "Another message",
                "receiver_id": 0,  # Not needed when conversation_id is provided
                "conversation_id": test_conversation.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Another message"
        assert data["conversation_id"] == test_conversation.id

    def test_send_message_to_nonexistent_user(self, client: TestClient, auth_headers):
        """Test sending message to nonexistent user fails."""
        response = client.post(
            "/api/messages/", headers=auth_headers, json={"content": "Hello?", "receiver_id": 99999}
        )
        assert response.status_code == 404
        assert "Receiver not found" in response.json()["detail"]

    def test_send_message_unauthorized(self, client: TestClient, test_user2):
        """Test sending message without auth fails."""
        response = client.post(
            "/api/messages/", json={"content": "Hello!", "receiver_id": test_user2.id}
        )
        assert response.status_code == 401


class TestGetConversationMessages:
    """Tests for getting conversation messages."""

    def test_get_messages_success(
        self, client: TestClient, auth_headers, test_conversation, test_message
    ):
        """Test getting messages from a conversation."""
        response = client.get(
            f"/api/messages/conversation/{test_conversation.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["data"]) == 1
        assert data["data"][0]["content"] == test_message.content

    def test_get_messages_pagination(
        self, client: TestClient, auth_headers, test_conversation, db_session, test_user
    ):
        """Test message pagination."""
        # Create multiple messages
        from app.models.sqlite_models import Message

        for i in range(25):
            msg = Message(
                conversation_id=test_conversation.id, sender_id=test_user.id, content=f"Message {i}"
            )
            db_session.add(msg)
        db_session.commit()

        # Get first page
        response = client.get(
            f"/api/messages/conversation/{test_conversation.id}?page=1&limit=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["data"]) == 10
        assert data["page"] == 1
        assert data["limit"] == 10

    def test_get_messages_not_participant(self, client: TestClient, auth_headers, db_session):
        """Test getting messages when not a participant fails."""
        from app.models.sqlite_models import Conversation

        # Create a conversation without the test user
        other_conv = Conversation()
        db_session.add(other_conv)
        db_session.commit()

        response = client.get(f"/api/messages/conversation/{other_conv.id}", headers=auth_headers)
        assert response.status_code == 403
        assert "not a participant" in response.json()["detail"]


class TestDeleteMessage:
    """Tests for deleting messages."""

    def test_delete_own_message(self, client: TestClient, auth_headers, test_message):
        """Test deleting own message succeeds."""
        response = client.delete(f"/api/messages/{test_message.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_deleted"] is True

    def test_delete_others_message(self, client: TestClient, auth_headers2, test_message):
        """Test deleting another user's message fails."""
        response = client.delete(f"/api/messages/{test_message.id}", headers=auth_headers2)
        assert response.status_code == 403
        assert "only delete your own messages" in response.json()["detail"]

    def test_delete_nonexistent_message(self, client: TestClient, auth_headers):
        """Test deleting nonexistent message fails."""
        response = client.delete("/api/messages/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateMessageStatus:
    """Tests for updating message status."""

    def test_update_status_to_delivered(self, client: TestClient, auth_headers2, test_message):
        """Test updating message status to delivered."""
        response = client.put(
            f"/api/messages/{test_message.id}/status",
            headers=auth_headers2,
            json={"status": "delivered"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "delivered"

    def test_update_status_to_read(self, client: TestClient, auth_headers2, test_message):
        """Test updating message status to read."""
        response = client.put(
            f"/api/messages/{test_message.id}/status",
            headers=auth_headers2,
            json={"status": "read"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "read"


class TestMarkConversationAsRead:
    """Tests for marking conversation as read."""

    def test_mark_as_read_success(
        self, client: TestClient, auth_headers2, test_conversation, test_message
    ):
        """Test marking all messages in conversation as read."""
        response = client.put(
            f"/api/messages/conversation/{test_conversation.id}/read", headers=auth_headers2
        )
        assert response.status_code == 200
        data = response.json()
        assert "marked_as_read" in data
        assert data["marked_as_read"] >= 1

    def test_mark_as_read_not_participant(self, client: TestClient, auth_headers, db_session):
        """Test marking as read when not participant fails."""
        from app.models.sqlite_models import Conversation

        other_conv = Conversation()
        db_session.add(other_conv)
        db_session.commit()

        response = client.put(
            f"/api/messages/conversation/{other_conv.id}/read", headers=auth_headers
        )
        assert response.status_code == 403

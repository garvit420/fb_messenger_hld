"""Conversation controller for conversation operations using SQLAlchemy."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from app.models.sqlite_models import Conversation, ConversationParticipant, Message, User
from app.schemas.conversation import (
    ConversationResponse,
    PaginatedConversationResponse,
    ParticipantResponse,
)


class ConversationController:
    """Controller for conversation operations."""

    async def get_user_conversations(
        self, db: Session, user: User, page: int = 1, limit: int = 20
    ) -> PaginatedConversationResponse:
        """Get all conversations for the authenticated user with pagination."""
        # Get conversation IDs the user is part of
        user_conversation_ids = (
            db.query(ConversationParticipant.conversation_id)
            .filter(ConversationParticipant.user_id == user.id)
            .subquery()
        )

        # Get total count
        total = (
            db.query(func.count(Conversation.id))
            .filter(Conversation.id.in_(user_conversation_ids))
            .scalar()
        )

        # Get conversations with pagination
        offset = (page - 1) * limit
        conversations = (
            db.query(Conversation)
            .filter(Conversation.id.in_(user_conversation_ids))
            .order_by(desc(Conversation.updated_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Build response with participants and last message
        conversation_responses = []
        for conv in conversations:
            # Get participants
            participants = self._get_conversation_participants(db, conv.id)

            # Get last message
            last_message = (
                db.query(Message)
                .filter(and_(Message.conversation_id == conv.id, Message.is_deleted.is_(False)))
                .order_by(desc(Message.created_at))
                .first()
            )

            conversation_responses.append(
                ConversationResponse(
                    id=conv.id,
                    participants=participants,
                    last_message_at=last_message.created_at if last_message else None,
                    last_message_content=last_message.content if last_message else None,
                    created_at=conv.created_at,
                )
            )

        return PaginatedConversationResponse(
            total=total, page=page, limit=limit, data=conversation_responses
        )

    async def get_conversation(
        self, db: Session, user: User, conversation_id: str
    ) -> ConversationResponse:
        """Get a specific conversation by ID."""
        # Verify user is a participant
        participant = (
            db.query(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == user.id,
                )
            )
            .first()
        )

        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a participant in this conversation",
            )

        # Get the conversation
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        # Get participants
        participants = self._get_conversation_participants(db, conversation_id)

        # Get last message
        last_message = (
            db.query(Message)
            .filter(and_(Message.conversation_id == conversation_id, Message.is_deleted.is_(False)))
            .order_by(desc(Message.created_at))
            .first()
        )

        return ConversationResponse(
            id=conversation.id,
            participants=participants,
            last_message_at=last_message.created_at if last_message else None,
            last_message_content=last_message.content if last_message else None,
            created_at=conversation.created_at,
        )

    def _get_conversation_participants(
        self, db: Session, conversation_id: str
    ) -> list[ParticipantResponse]:
        """Get all participants for a conversation."""
        participants = (
            db.query(User)
            .join(ConversationParticipant)
            .filter(ConversationParticipant.conversation_id == conversation_id)
            .all()
        )

        return [
            ParticipantResponse(
                user_id=p.id,
                username=p.username,
                display_name=p.display_name,
                avatar_url=p.avatar_url,
                is_online=p.is_online,
            )
            for p in participants
        ]

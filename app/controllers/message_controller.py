"""Message controller for message operations using SQLAlchemy."""

from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.sqlite_models import Message, Conversation, ConversationParticipant, User
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageStatusUpdate,
    PaginatedMessageResponse,
    MessageStatus,
)


class MessageController:
    """Controller for message operations."""

    async def send_message(
        self, db: Session, sender: User, message_data: MessageCreate
    ) -> MessageResponse:
        """Send a new message."""
        # Get or create conversation
        conversation_id = message_data.conversation_id

        if conversation_id:
            # Verify conversation exists and user is a participant
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
                )

            # Check if sender is a participant
            participant = (
                db.query(ConversationParticipant)
                .filter(
                    and_(
                        ConversationParticipant.conversation_id == conversation_id,
                        ConversationParticipant.user_id == sender.id,
                    )
                )
                .first()
            )

            if not participant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a participant in this conversation",
                )
        else:
            # Check if receiver exists
            receiver = db.query(User).filter(User.id == message_data.receiver_id).first()
            if not receiver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found"
                )

            # Find existing conversation between these users
            conversation = self._find_or_create_conversation(
                db, sender.id, message_data.receiver_id
            )
            conversation_id = conversation.id

        # Create message
        new_message = Message(
            conversation_id=conversation_id,
            sender_id=sender.id,
            content=message_data.content,
            status=MessageStatus.SENT.value,
        )

        db.add(new_message)

        # Update conversation timestamp
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(new_message)

        return MessageResponse.model_validate(new_message)

    def _find_or_create_conversation(
        self, db: Session, user1_id: int, user2_id: int
    ) -> Conversation:
        """Find existing conversation between two users or create a new one."""
        # Find conversations where user1 is a participant
        user1_convos = (
            db.query(ConversationParticipant.conversation_id)
            .filter(ConversationParticipant.user_id == user1_id)
            .subquery()
        )

        # Find conversation where user2 is also a participant
        existing_convo = (
            db.query(ConversationParticipant.conversation_id)
            .filter(
                and_(
                    ConversationParticipant.user_id == user2_id,
                    ConversationParticipant.conversation_id.in_(user1_convos),
                )
            )
            .first()
        )

        if existing_convo:
            return db.query(Conversation).filter(Conversation.id == existing_convo[0]).first()

        # Create new conversation
        conversation = Conversation()
        db.add(conversation)
        db.flush()

        # Add participants
        participant1 = ConversationParticipant(conversation_id=conversation.id, user_id=user1_id)
        participant2 = ConversationParticipant(conversation_id=conversation.id, user_id=user2_id)

        db.add(participant1)
        db.add(participant2)
        db.flush()

        return conversation

    async def get_conversation_messages(
        self, db: Session, user: User, conversation_id: str, page: int = 1, limit: int = 20
    ) -> PaginatedMessageResponse:
        """Get messages in a conversation with pagination."""
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

        # Get total count
        total = (
            db.query(func.count(Message.id))
            .filter(and_(Message.conversation_id == conversation_id, Message.is_deleted.is_(False)))
            .scalar()
        )

        # Get messages with pagination
        offset = (page - 1) * limit
        messages = (
            db.query(Message)
            .filter(and_(Message.conversation_id == conversation_id, Message.is_deleted.is_(False)))
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return PaginatedMessageResponse(
            total=total,
            page=page,
            limit=limit,
            data=[MessageResponse.model_validate(m) for m in messages],
        )

    async def get_messages_before_timestamp(
        self,
        db: Session,
        user: User,
        conversation_id: str,
        before_timestamp: datetime,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedMessageResponse:
        """Get messages before a specific timestamp."""
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

        # Get total count
        total = (
            db.query(func.count(Message.id))
            .filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.is_deleted.is_(False),
                    Message.created_at < before_timestamp,
                )
            )
            .scalar()
        )

        # Get messages with pagination
        offset = (page - 1) * limit
        messages = (
            db.query(Message)
            .filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.is_deleted.is_(False),
                    Message.created_at < before_timestamp,
                )
            )
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return PaginatedMessageResponse(
            total=total,
            page=page,
            limit=limit,
            data=[MessageResponse.model_validate(m) for m in messages],
        )

    async def delete_message(self, db: Session, user: User, message_id: str) -> MessageResponse:
        """Soft delete a message (only sender can delete)."""
        message = db.query(Message).filter(Message.id == message_id).first()

        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

        if message.sender_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own messages",
            )

        message.is_deleted = True
        message.deleted_at = datetime.utcnow()
        message.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)

        return MessageResponse.model_validate(message)

    async def update_message_status(
        self, db: Session, user: User, message_id: str, status_data: MessageStatusUpdate
    ) -> MessageResponse:
        """Update message status (delivered/read)."""
        message = db.query(Message).filter(Message.id == message_id).first()

        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

        # Verify user is a participant in the conversation
        participant = (
            db.query(ConversationParticipant)
            .filter(
                and_(
                    ConversationParticipant.conversation_id == message.conversation_id,
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

        message.status = status_data.status.value
        message.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)

        return MessageResponse.model_validate(message)

    async def mark_conversation_as_read(
        self, db: Session, user: User, conversation_id: str
    ) -> dict:
        """Mark all messages in a conversation as read."""
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

        # Update all unread messages not sent by the user
        updated_count = (
            db.query(Message)
            .filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.sender_id != user.id,
                    Message.status != MessageStatus.READ.value,
                    Message.is_deleted.is_(False),
                )
            )
            .update({"status": MessageStatus.READ.value, "updated_at": datetime.utcnow()})
        )

        db.commit()

        return {"marked_as_read": updated_count}

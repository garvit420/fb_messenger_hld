"""Message API routes with authentication."""

from fastapi import APIRouter, Depends, Query, Path, Body, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.sqlite_client import get_db
from app.core.dependencies import get_current_user
from app.controllers.message_controller import MessageController
from app.models.sqlite_models import User
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageStatusUpdate,
    PaginatedMessageResponse,
)

router = APIRouter(prefix="/api/messages", tags=["Messages"])


def get_message_controller() -> MessageController:
    """Dependency to get MessageController instance."""
    return MessageController()


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message: MessageCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: MessageController = Depends(get_message_controller),
) -> MessageResponse:
    """Send a message from the authenticated user."""
    return await controller.send_message(db, current_user, message)


@router.get("/conversation/{conversation_id}", response_model=PaginatedMessageResponse)
async def get_conversation_messages(
    conversation_id: str = Path(..., description="ID of the conversation"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Number of messages per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: MessageController = Depends(get_message_controller),
) -> PaginatedMessageResponse:
    """Get all messages in a conversation with pagination."""
    return await controller.get_conversation_messages(
        db, current_user, conversation_id, page, limit
    )


@router.get("/conversation/{conversation_id}/before", response_model=PaginatedMessageResponse)
async def get_messages_before_timestamp(
    conversation_id: str = Path(..., description="ID of the conversation"),
    before_timestamp: datetime = Query(..., description="Get messages before this timestamp"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Number of messages per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: MessageController = Depends(get_message_controller),
) -> PaginatedMessageResponse:
    """Get messages in a conversation before a specific timestamp."""
    return await controller.get_messages_before_timestamp(
        db, current_user, conversation_id, before_timestamp, page, limit
    )


@router.delete("/{message_id}", response_model=MessageResponse)
async def delete_message(
    message_id: str = Path(..., description="ID of the message to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: MessageController = Depends(get_message_controller),
) -> MessageResponse:
    """Soft delete a message (only sender can delete)."""
    return await controller.delete_message(db, current_user, message_id)


@router.put("/{message_id}/status", response_model=MessageResponse)
async def update_message_status(
    message_id: str = Path(..., description="ID of the message"),
    status_data: MessageStatusUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: MessageController = Depends(get_message_controller),
) -> MessageResponse:
    """Update message status (delivered/read)."""
    return await controller.update_message_status(db, current_user, message_id, status_data)


@router.put("/conversation/{conversation_id}/read")
async def mark_conversation_as_read(
    conversation_id: str = Path(..., description="ID of the conversation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: MessageController = Depends(get_message_controller),
):
    """Mark all messages in a conversation as read."""
    return await controller.mark_conversation_as_read(db, current_user, conversation_id)

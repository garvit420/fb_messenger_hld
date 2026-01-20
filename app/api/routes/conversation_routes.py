"""Conversation API routes with authentication."""
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.db.sqlite_client import get_db
from app.core.dependencies import get_current_user
from app.controllers.conversation_controller import ConversationController
from app.models.sqlite_models import User
from app.schemas.conversation import (
    ConversationResponse,
    PaginatedConversationResponse
)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


def get_conversation_controller() -> ConversationController:
    """Dependency to get ConversationController instance."""
    return ConversationController()


@router.get("/", response_model=PaginatedConversationResponse)
async def get_user_conversations(
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Number of conversations per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: ConversationController = Depends(get_conversation_controller)
) -> PaginatedConversationResponse:
    """Get all conversations for the authenticated user with pagination."""
    return await controller.get_user_conversations(db, current_user, page, limit)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str = Path(..., description="ID of the conversation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    controller: ConversationController = Depends(get_conversation_controller)
) -> ConversationResponse:
    """Get a specific conversation by ID."""
    return await controller.get_conversation(db, current_user, conversation_id)

"""Pydantic schemas for conversation-related operations."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.message import MessageResponse


class ParticipantResponse(BaseModel):
    """Schema for conversation participant."""
    user_id: int = Field(..., description="ID of the participant")
    username: str = Field(..., description="Username of the participant")
    display_name: Optional[str] = Field(None, description="Display name of the participant")
    avatar_url: Optional[str] = Field(None, description="Avatar URL of the participant")
    is_online: bool = Field(False, description="Whether the participant is online")

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: str = Field(..., description="Unique ID of the conversation")
    participants: List[ParticipantResponse] = Field(..., description="List of participants")
    last_message_at: Optional[datetime] = Field(None, description="Timestamp of the last message")
    last_message_content: Optional[str] = Field(None, description="Content of the last message")
    created_at: datetime = Field(..., description="Timestamp when conversation was created")


class ConversationDetail(ConversationResponse):
    """Schema for detailed conversation response with messages."""
    messages: List[MessageResponse] = Field(..., description="List of messages in conversation")


class PaginatedConversationRequest(BaseModel):
    """Schema for paginated conversation request."""
    page: int = Field(1, description="Page number for pagination")
    limit: int = Field(20, description="Number of items per page")


class PaginatedConversationResponse(BaseModel):
    """Schema for paginated conversation response."""
    total: int = Field(..., description="Total number of conversations")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    data: List[ConversationResponse] = Field(..., description="List of conversations")

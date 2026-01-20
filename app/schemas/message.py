"""Pydantic schemas for message-related operations."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageStatus(str, Enum):
    """Message delivery status."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class MessageBase(BaseModel):
    """Base schema for message data."""
    content: str = Field(..., description="Content of the message")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    receiver_id: int = Field(..., description="ID of the receiver")
    conversation_id: Optional[str] = Field(None, description="ID of an existing conversation")


class MessageStatusUpdate(BaseModel):
    """Schema for updating message status."""
    status: MessageStatus = Field(..., description="New status for the message")


class MessageResponse(MessageBase):
    """Schema for message response."""
    id: str = Field(..., description="Unique ID of the message")
    sender_id: int = Field(..., description="ID of the sender")
    conversation_id: str = Field(..., description="ID of the conversation")
    status: MessageStatus = Field(MessageStatus.SENT, description="Message delivery status")
    is_deleted: bool = Field(False, description="Whether the message is deleted")
    created_at: datetime = Field(..., description="Timestamp when message was created")
    updated_at: datetime = Field(..., description="Timestamp when message was last updated")

    model_config = {"from_attributes": True}


class PaginatedMessageRequest(BaseModel):
    """Schema for paginated message request."""
    page: int = Field(1, description="Page number for pagination")
    limit: int = Field(20, description="Number of items per page")
    before_timestamp: Optional[datetime] = Field(None, description="Get messages before this timestamp")


class PaginatedMessageResponse(BaseModel):
    """Schema for paginated message response."""
    total: int = Field(..., description="Total number of messages")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    data: List[MessageResponse] = Field(..., description="List of messages")

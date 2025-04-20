from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
import uuid

from app.schemas.message import MessageCreate, MessageResponse, PaginatedMessageResponse
from app.models.cassandra_models import MessageModel, ConversationModel

class MessageController:
    """
    Controller for handling message operations
    """
    
    async def send_message(self, message_data: MessageCreate) -> MessageResponse:
        """
        Send a message from one user to another
        
        Args:
            message_data: The message data including content, sender_id, and receiver_id
            
        Returns:
            The created message with metadata (IDs as UUIDs)
        
        Raises:
            HTTPException: If message sending fails
        """
        try:
            # Create the message using the MessageModel
            message = MessageModel.create_message(
                sender_id=message_data.sender_id,
                receiver_id=message_data.receiver_id,
                content=message_data.content
            )

            print(f"Message created: {message}")
            
            # Return the MessageResponse with UUIDs
            return MessageResponse(
                id=message['id'],
                content=message['content'],
                sender_id=message['sender_id'],
                receiver_id=message['receiver_id'],
                created_at=message['created_at'],
                conversation_id=message['conversation_id']
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}"
            )
    
    async def get_conversation_messages(
        self, 
        conversation_id: uuid.UUID, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedMessageResponse:
        """
        Get all messages in a conversation with pagination
        
        Args:
            conversation_id: ID of the conversation (UUID)
            page: Page number
            limit: Number of messages per page
            
        Returns:
            Paginated list of messages
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        try:
            # Get messages using pagination with UUID
            result = MessageModel.get_conversation_messages(
                conversation_id=conversation_id,
                limit=limit
            )
            
            # Convert the model data to response schema
            messages = []
            for msg in result['data']:
                messages.append(MessageResponse(
                    id=msg['id'],
                    content=msg['content'],
                    sender_id=msg['sender_id'],
                    receiver_id=msg['receiver_id'],
                    created_at=msg['created_at'],
                    conversation_id=conversation_id # Use the UUID passed in
                ))
            
            # Return paginated response
            return PaginatedMessageResponse(
                total=result['total'],
                page=page,
                limit=limit,
                data=messages
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversation messages: {str(e)}"
            )
    
    async def get_messages_before_timestamp(
        self, 
        conversation_id: uuid.UUID, 
        before_timestamp: datetime,
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedMessageResponse:
        """
        Get messages in a conversation before a specific timestamp with pagination
        
        Args:
            conversation_id: ID of the conversation (UUID)
            before_timestamp: Get messages before this timestamp
            page: Page number
            limit: Number of messages per page
            
        Returns:
            Paginated list of messages
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        try:
            # Get messages before timestamp with UUID
            result = MessageModel.get_messages_before_timestamp(
                conversation_id=conversation_id,
                before_timestamp=before_timestamp,
                limit=limit
            )
            
            # Convert the model data to response schema
            messages = []
            for msg in result['data']:
                messages.append(MessageResponse(
                    id=msg['id'],
                    content=msg['content'],
                    sender_id=msg['sender_id'],
                    receiver_id=msg['receiver_id'],
                    created_at=msg['created_at'],
                    conversation_id=conversation_id # Use the UUID passed in
                ))
            
            # Return paginated response
            return PaginatedMessageResponse(
                total=result['total'],
                page=page,
                limit=limit,
                data=messages
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get messages before timestamp: {str(e)}"
            ) 
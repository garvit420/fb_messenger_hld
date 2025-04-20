"""
Sample models for interacting with Cassandra tables.
Students should implement these models based on their database schema design.
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.db.cassandra_client import cassandra_client

class MessageModel:
    """
    Message model for interacting with the messages table.
    Implements methods for creating and retrieving messages.
    """
    
    @staticmethod
    def create_message(
        sender_id: int,
        receiver_id: int,
        content: str,
        conversation_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Create a new message.
        
        Args:
            sender_id: ID of the message sender (int)
            receiver_id: ID of the message receiver (int)
            content: Content of the message
            conversation_id: Optional ID of the existing conversation (UUID)
            
        Returns:
            The created message data
        """
        # Use current timestamp for the message
        timestamp = datetime.utcnow()
        
        # Generate a timeuuid for the message
        message_id = uuid.uuid1()
        
        # If no conversation_id is provided, create one
        if not conversation_id:
            conversation = ConversationModel.create_conversation(sender_id, receiver_id)
            conversation_id = conversation['conversation_id']
        
        # Insert the message into the messages_by_conversation table
        # Format query execution
        cassandra_client.execute(
            """
            INSERT INTO messages_by_conversation (
                conversation_id, 
                message_id, 
                sender_id, 
                receiver_id, 
                content, 
                timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                conversation_id,
                message_id,
                sender_id,
                receiver_id,
                content,
                timestamp
            )
        )
        
        # Update the last_message_timestamp in the conversations_by_user table
        # We cannot UPDATE primary key columns (last_message_timestamp). 
        # Instead, we INSERT a new row. Cassandra's upsert behavior handles this.
        insert_conversation_query = """
            INSERT INTO conversations_by_user (user_id, conversation_id, partner_id, last_message_timestamp)
            VALUES (%s, %s, %s, %s)
        """

        # Insert/Update entry for sender
        cassandra_client.execute(
            insert_conversation_query,
            (
                sender_id,
                conversation_id,
                receiver_id, # Partner ID
                timestamp # New last_message_timestamp
            )
        )
        
        # Insert/Update entry for receiver
        cassandra_client.execute(
            insert_conversation_query,
            (
                receiver_id,
                conversation_id,
                sender_id, # Partner ID
                timestamp # New last_message_timestamp
            )
        )

        # Return the message data with correct types
        return {
            'id': message_id, # UUID
            'conversation_id': conversation_id, # UUID
            'sender_id': sender_id, # int
            'receiver_id': receiver_id, # int
            'content': content,
            'created_at': timestamp
        }
    
    @staticmethod
    def get_conversation_messages(
        conversation_id: uuid.UUID,
        page_state: Optional[bytes] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get messages for a conversation with pagination.
        
        Args:
            conversation_id: ID of the conversation (UUID)
            page_state: Token for pagination continuation
            limit: Number of messages to return
            
        Returns:
            Dict containing messages and pagination token
        """
        # Format query execution (excluding paging state part)
        query = """
            SELECT * FROM messages_by_conversation 
            WHERE conversation_id = %s 
            LIMIT %s
        """
        params = (
            conversation_id,
            limit
        )
        
        # Use paging state for continuation if provided
        session = cassandra_client.get_session()
        if page_state:
            statement = session.prepare(query.replace("%s", "?")) # Use ? for prepared statements
            statement.fetch_size = limit
            bound = statement.bind(params)
            result = session.execute(bound, paging_state=page_state) # Keep synchronous for session.execute
        else:
            # Use synchronous execute
            result = cassandra_client.execute(query, params)
            
        # Get the next paging state
        next_page_state = getattr(result, 'paging_state', None)
        
        # Format the messages, converting user IDs back to int
        messages = []
        for row in result:
            messages.append({
                'id': row.get('message_id'), # UUID
                'conversation_id': row.get('conversation_id'), # UUID
                'sender_id': row.get('sender_id'), 
                'receiver_id': row.get('receiver_id'), 
                'content': row.get('content'),
                'created_at': row.get('timestamp')
            })
        
        # Count total messages in conversation (for pagination metadata)
        # Format query execution
        count_result = cassandra_client.execute(
            """
            SELECT COUNT(*) as total FROM messages_by_conversation 
            WHERE conversation_id = %s
            """,
            (conversation_id,)
        )
        total = count_result[0]['total'] if count_result and count_result[0] else 0
        
        return {
            'data': messages,
            'total': total,
            'page_state': next_page_state
        }
    
    @staticmethod
    def get_messages_before_timestamp(
        conversation_id: uuid.UUID,
        before_timestamp: datetime,
        page_state: Optional[bytes] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get messages before a timestamp with pagination.
        
        Args:
            conversation_id: ID of the conversation (UUID)
            before_timestamp: Get messages before this timestamp
            page_state: Token for pagination continuation
            limit: Number of messages to return
            
        Returns:
            Dict containing messages and pagination token
        """
        # Convert before_timestamp to a timeuuid if it's just a datetime
        # Note: This might need adjustment based on how message_id is generated/compared
        before_uuid = uuid.uuid1(node=0, clock_seq=int(before_timestamp.timestamp() * 1e7))
        
        # Format query execution (excluding paging state part)
        query = """
            SELECT * FROM messages_by_conversation 
            WHERE conversation_id = %s 
            AND message_id < %s
            LIMIT %s
        """
        params = (
            conversation_id,
            before_uuid,
            limit
        )
        
        # Use paging state for continuation if provided
        session = cassandra_client.get_session()
        if page_state:
            statement = session.prepare(query.replace("%s", "?")) # Use ? for prepared statements
            statement.fetch_size = limit
            bound = statement.bind(params)
            result = session.execute(bound, paging_state=page_state) # Keep synchronous for session.execute
        else:
            # Use synchronous execute
            result = cassandra_client.execute(query, params)
            
        # Get the next paging state
        next_page_state = getattr(result, 'paging_state', None)
        
        # Format the messages, converting user IDs back to int
        messages = []
        for row in result:
            messages.append({
                'id': row.get('message_id'), # UUID
                'conversation_id': row.get('conversation_id'), # UUID
                'sender_id': row.get('sender_id'), 
                'receiver_id': row.get('receiver_id'), 
                'content': row.get('content'),
                'created_at': row.get('timestamp')
            })
        
        # Count messages before the timestamp
        # Note: Count query might need adjustment depending on exact schema/indexing
        # Format query execution
        count_result = cassandra_client.execute(
            """
            SELECT COUNT(*) as total FROM messages_by_conversation 
            WHERE conversation_id = %s AND message_id < %s
            """,
            (
                conversation_id,
                before_uuid
            )
        )
        total = count_result[0]['total'] if count_result and count_result[0] else 0
        
        return {
            'data': messages,
            'total': total,
            'page_state': next_page_state
        }


class ConversationModel:
    """
    Conversation model for interacting with the conversations-related tables.
    Implements methods for retrieving and creating conversations.
    """
    
    @staticmethod
    def get_user_conversations(
        user_id: int,
        page_state: Optional[bytes] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get conversations for a user with pagination.
        
        Args:
            user_id: ID of the user (int)
            page_state: Token for pagination continuation
            limit: Number of conversations to return
            
        Returns:
            Dict containing conversations and pagination token
        """
        # Format query execution (excluding paging state part)
        query = """
            SELECT conversation_id, partner_id, last_message_timestamp 
            FROM conversations_by_user 
            WHERE user_id = %s 
            LIMIT %s
        """ # Note: Removed user1_id, user2_id as they are not in the schema
        params = (
            user_id,
            limit
        )
        
        # Use paging state for continuation if provided
        session = cassandra_client.get_session()
        if page_state:
            statement = session.prepare(query.replace("%s", "?")) # Use ? for prepared statements
            statement.fetch_size = limit
            bound = statement.bind(params)
            result = session.execute(bound, paging_state=page_state) # Keep synchronous for session.execute
        else:
            # Use synchronous execute
            result = cassandra_client.execute(query, params)
            
        # Get the next paging state
        next_page_state = getattr(result, 'paging_state', None)
        
        conversations = []
        for row in result:
            # Fetch last message content if needed (example, might be inefficient)
            # This requires knowing the message schema and how to query it
            last_msg_content = None
            # Fetch the latest message for this conversation to get content
            # This could be optimized, potentially by adding last_message_content to conversations_by_user
            try:
                msg_result = cassandra_client.execute(
                    """
                    SELECT content FROM messages_by_conversation 
                    WHERE conversation_id = %s LIMIT 1
                    """, 
                    (row.get('conversation_id'),)
                )
                if msg_result:
                    last_msg_content = msg_result[0].get('content')
            except Exception: # Handle potential errors fetching last message
                last_msg_content = "[Error fetching message]"

            conversations.append({
                'id': row.get('conversation_id'), # UUID
                # Determine user1/user2 based on current user_id and partner_id
                'user1_id': user_id, 
                'user2_id': row.get('partner_id'), 
                'last_message_at': row.get('last_message_timestamp'),
                'last_message_content': last_msg_content 
            })
            
        # Count total conversations for the user
        # Format query execution
        count_result = cassandra_client.execute(
            """
            SELECT COUNT(*) as total FROM conversations_by_user 
            WHERE user_id = %s
            """,
            (user_id,)
        )
        total = count_result[0]['total'] if count_result and count_result[0] else 0

        return {
            'data': conversations,
            'total': total,
            'page_state': next_page_state
        }
    
    @staticmethod
    def get_conversation(conversation_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Get a specific conversation by its ID.
        
        Args:
            conversation_id: ID of the conversation (UUID)
            
        Returns:
            Conversation data or None if not found
        """
        result = cassandra_client.execute(
            """
            SELECT * 
            FROM messages_by_conversation 
            WHERE conversation_id = %s LIMIT 1
            """, # Fetching one record is enough to get IDs and timestamp
            (conversation_id,)
        )
        row = result[0] if result else None
        
        if row:
            return {
                'id': conversation_id, # UUID from input
                'user1_id': row.get('sender_id'), 
                'user2_id': row.get('receiver_id'), 
                'last_message_at': row.get('timestamp'),
                'last_message_content': row.get('content')
            }
        return None
    
    @staticmethod
    def create_conversation(
        user1_id: int,
        user2_id: int
    ) -> Dict[str, Any]:
        """
        Create or retrieve a conversation between two users.
        Handles ordering of user IDs to ensure uniqueness.
        Generates a TIMEUUID for the conversation ID.
        
        Args:
            user1_id: ID of the first user (int)
            user2_id: ID of the second user (int)
            
        Returns:
            Conversation details (including conversation_id as TIMEUUID)
        """
        # Check if conversation exists - this is complex without a dedicated lookup table
        # For simplicity, we'll just create a new one or rely on idempotency if called again
        
        conversation_id = uuid.uuid1() 
        timestamp = datetime.utcnow() # Use creation time for initial last_message_timestamp
         
        # Insert/Update entries in conversations_by_user table
        insert_query = """
            INSERT INTO conversations_by_user (user_id, conversation_id, partner_id, last_message_timestamp) 
            VALUES (%s, %s, %s, %s)
        """
          
        # Insert for user1
        cassandra_client.execute(
            insert_query,
            (
                user1_id, 
                conversation_id, 
                user2_id, # Partner ID for user1 is user2
                timestamp 
            )
        )
          
        # Insert for user2
        cassandra_client.execute(
            insert_query,
            (
                user2_id, 
                conversation_id,
                user1_id, # Partner ID for user2 is user1
                timestamp
            )
        )
        
        return {
            'conversation_id': conversation_id, # UUID
            'user1_id': user1_id, # int
            'user2_id': user2_id # int
        } 
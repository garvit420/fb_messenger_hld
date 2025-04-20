"""
Script to generate test data for the Messenger application.
This script is a skeleton for students to implement.
"""
import os
import uuid
import logging
import random
from datetime import datetime, timedelta
from cassandra.cluster import Cluster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cassandra connection settings
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "localhost")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT", "9042"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "messenger")

# Test data configuration
NUM_USERS = 10  # Number of users to create
NUM_CONVERSATIONS = 15  # Number of conversations to create
MAX_MESSAGES_PER_CONVERSATION = 50  # Maximum number of messages per conversation

def connect_to_cassandra():
    """Connect to Cassandra cluster."""
    logger.info("Connecting to Cassandra...")
    try:
        cluster = Cluster([CASSANDRA_HOST])
        session = cluster.connect(CASSANDRA_KEYSPACE)
        logger.info("Connected to Cassandra!")
        return cluster, session
    except Exception as e:
        logger.error(f"Failed to connect to Cassandra: {str(e)}")
        raise

def generate_test_data(session):
    """
    Generate test data in Cassandra.
    
    Students should implement this function to generate test data based on their schema design.
    The function should create:
    - Users (with IDs 1-NUM_USERS)
    - Conversations between random pairs of users
    - Messages in each conversation with realistic timestamps
    """
    logger.info("Generating test data...")
    
    # TODO: Students should implement the test data generation logic
    # Hints:
    # 1. Create a set of user IDs (ints from 1 to NUM_USERS)
    #    user_ids = set(range(1, NUM_USERS + 1))
    # 2. Create conversations between random pairs of users.
    #    - Ensure user IDs in pairs are ordered (e.g., user1_id < user2_id) if your model requires it.
    #    - Generate a unique conversation_id for each pair using uuid.uuid4().
    #    - Store conversation details in relevant tables (e.g., conversations_by_user).
    #    Example:
    #    for _ in range(NUM_CONVERSATIONS):
    #        user1, user2 = random.sample(list(user_ids), 2)
    #        if user1 > user2: user1, user2 = user2, user1 # Ensure order
    #        conversation_id = uuid.uuid4()
    #        timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 30))
    #        # Insert into conversations_by_user for user1
    #        # Insert into conversations_by_user for user2
    #        # Store conversation_id along with user IDs
    #
    # 3. For each conversation, generate a random number of messages.
    #    - Generate message_id using uuid.uuid1() (time-based) or uuid.uuid4() (random).
    #      uuid.uuid1() is generally preferred for time-ordered data like messages.
    #    - Use realistic timestamps (e.g., slightly varying around the conversation's last_message_timestamp).
    #    - Insert message details into the messages_by_conversation table.
    #    Example (inside conversation loop):
    #    num_messages = random.randint(1, MAX_MESSAGES_PER_CONVERSATION)
    #    last_msg_time = timestamp
    #    for _ in range(num_messages):
    #        msg_sender = random.choice([user1, user2])
    #        msg_receiver = user2 if msg_sender == user1 else user1
    #        msg_time = last_msg_time + timedelta(seconds=random.randint(1, 3600))
    #        message_id = uuid.uuid1() # TimeUUID
    #        content = f"Test message {_}"
    #        # Insert into messages_by_conversation
    #        last_msg_time = msg_time
    #    # Update conversation's last_message_timestamp after adding messages
    #
    # 4. Ensure all relevant tables are updated consistently based on your schema design.

    logger.info(f"Generated {NUM_CONVERSATIONS} conversations with messages (placeholders)")
    logger.info(f"User IDs range from 1 to {NUM_USERS}")
    logger.info("Use these IDs for testing the API endpoints")

def main():
    """Main function to generate test data."""
    cluster = None
    
    try:
        # Connect to Cassandra
        cluster, session = connect_to_cassandra()
        
        # Generate test data
        generate_test_data(session)
        
        logger.info("Test data generation completed successfully!")
    except Exception as e:
        logger.error(f"Error generating test data: {str(e)}")
    finally:
        if cluster:
            cluster.shutdown()
            logger.info("Cassandra connection closed")

if __name__ == "__main__":
    main() 
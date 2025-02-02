import os
import atexit
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime

# Load environment variables
load_dotenv()

class MongoDB:
    _instance = None
    _db = None  # Store the database instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._initialize_connection()
            # Register cleanup on exit
            atexit.register(cls._instance.cleanup)
        return cls._instance

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def _initialize_connection(self):
        try:
            # Use the exact connection string provided by DigitalOcean
            uri = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}/{os.getenv('MONGO_DB')}?authSource=admin&tls=true"
            
            # Create MongoDB client
            self.client = MongoClient(uri)
            
            # Store database instance
            self._db = self.client[os.getenv('MONGO_DB')]
            
            # Test connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    def get_conversation_history(self, call_uuid):
        """Get conversation history for a specific call"""
        try:
            conversation = self._db.conversations.find_one({'call_uuid': call_uuid})
            return conversation['messages'] if conversation else []
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

    def update_conversation(self, call_uuid, user_message=None, assistant_message=None):
        """Update conversation history with new messages"""
        try:
            # Get current timestamp
            timestamp = datetime.utcnow().isoformat()
            
            # Create update operations
            update_ops = []
            
            if user_message:
                update_ops.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": timestamp
                })
                
            if assistant_message:
                update_ops.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "timestamp": timestamp
                })
                
            if update_ops:
                # Update or create conversation document
                current_time = datetime.utcnow().isoformat()
                self._db.conversations.update_one(
                    {'call_uuid': call_uuid},
                    {
                        '$push': {'messages': {'$each': update_ops}},
                        '$setOnInsert': {'created_at': current_time},
                        '$set': {'updated_at': current_time}
                    },
                    upsert=True
                )
                
        except Exception as e:
            print(f"Error updating conversation: {e}")

    def get_db(self):
        """Get the database instance"""
        return self._db

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'client'):
            try:
                self.client.close()
                print("MongoDB connection closed gracefully.")
            except Exception as e:
                print(f"Error while closing MongoDB connection: {e}")

    def close_connection(self):
        """Close the MongoDB connection (deprecated, use cleanup instead)"""
        self.cleanup() 
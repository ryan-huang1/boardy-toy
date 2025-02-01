import os
import atexit
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

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
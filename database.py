import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Load environment variables
load_dotenv()

class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        try:
            # Use the exact connection string provided by DigitalOcean
            uri = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}/{os.getenv('MONGO_DB')}?authSource=admin&tls=true"
            
            # Create MongoDB client
            self.client = MongoClient(uri)
            
            # Get database
            self.db = self.client[os.getenv('MONGO_DB')]
            
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
        return self.db

    def close_connection(self):
        """Close the MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            print("MongoDB connection closed.") 
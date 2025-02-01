from flask import Flask, jsonify, request
from flask_cors import CORS
from database import MongoDB
from embeddings import EmbeddingGenerator
import signal
import sys
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print('\nShutting down server gracefully...')
    # Cleanup MongoDB connection
    MongoDB().cleanup()
    print('Server shutdown complete.')
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize MongoDB connection at startup
try:
    MongoDB().get_db()
except Exception as e:
    print(f"Failed to initialize MongoDB connection: {e}")
    sys.exit(1)

# Initialize SBERT model at server start
print("Initializing SBERT model...")
EmbeddingGenerator.initialize()
print("SBERT model initialization complete!")

# Register person routes
from routes.person import person_bp
app.register_blueprint(person_bp, url_prefix='/api/person')

@app.route('/health')
def health_check():
    """Health check endpoint for DigitalOcean"""
    return jsonify({
        'status': 'healthy',
        'message': 'Service is running'
    })

@app.route('/test-db')
def test_db():
    try:
        # Get database instance
        db = MongoDB().get_db()
        
        # Test connection by running a command
        db.command('ping')
        
        return jsonify({
            'status': 'success',
            'message': 'Successfully connected to MongoDB!',
            'database_name': db.name
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    try:
        # Get port from environment variable or default to 5001
        port = int(os.environ.get('PORT', 5001))
        
        # Run the Flask development server
        app.run(debug=True, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt...")
    finally:
        # Ensure cleanup happens even if app.run() raises an exception
        MongoDB().cleanup() 
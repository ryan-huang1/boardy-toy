from flask import Flask, jsonify
from flask_cors import CORS
from database import MongoDB

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Basic setup for the Boardy project. No routes or additional configuration added yet.

# Example endpoint
@app.route('/hello')
def hello():
    return 'Hello, World!'

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
    app.run(debug=True, host='0.0.0.0', port=5001) 
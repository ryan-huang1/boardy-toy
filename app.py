from flask import Flask, jsonify, request
from flask_cors import CORS
from database import MongoDB

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register person routes
from routes.person import person_bp
app.register_blueprint(person_bp, url_prefix='/api/person')

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
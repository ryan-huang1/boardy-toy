from flask import Flask, jsonify, request
from flask_cors import CORS
from database import MongoDB
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Phone number validation regex
PHONE_REGEX = re.compile(r'^\+[1-9]\d{1,14}$')

def validate_phone_number(phone_number):
    """Validate phone number format using E.164 standard"""
    return bool(PHONE_REGEX.match(phone_number))

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

@app.route('/api/person/create', methods=['POST'])
def create_person():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('phoneNumber'):
            return jsonify({
                'success': False,
                'error': 'Phone number is required',
                'code': 400
            }), 400
            
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Name is required',
                'code': 400
            }), 400
            
        # Validate phone number format
        if not validate_phone_number(data['phoneNumber']):
            return jsonify({
                'success': False,
                'error': 'Invalid phone number format',
                'code': 400
            }), 400
            
        # Get database instance
        db = MongoDB().get_db()
        
        # Check if phone number already exists
        if db.persons.find_one({'phoneNumber': data['phoneNumber']}):
            return jsonify({
                'success': False,
                'error': 'Phone number already exists',
                'code': 409
            }), 409
            
        # Prepare person document
        now = datetime.utcnow()
        person = {
            'phoneNumber': data['phoneNumber'],
            'name': data['name'],
            'interests': data.get('interests', []),
            'skills': data.get('skills', []),
            'bio': data.get('bio', ''),
            'location': data.get('location', ''),
            'vectorEmbedding': [],  # TODO: Implement embedding generation
            'createdAt': now,
            'updatedAt': now
        }
        
        # Insert person into database
        result = db.persons.insert_one(person)
        
        # Remove _id from response
        person.pop('_id', None)
        
        return jsonify({
            'success': True,
            'message': 'Person created successfully',
            'data': person
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500

@app.route('/api/person/list', methods=['GET'])
def list_persons():
    try:
        # Get database instance
        db = MongoDB().get_db()
        
        # Get pagination parameters from query string
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
            
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        # Get total count of documents
        total_count = db.persons.count_documents({})
        
        # Get paginated results
        cursor = db.persons.find({}).skip(skip).limit(per_page)
        
        # Convert cursor to list and remove _id from each document
        persons = []
        for person in cursor:
            person.pop('_id', None)
            person.pop('vectorEmbedding', None)  # Remove vector embedding from response
            persons.append(person)
            
        return jsonify({
            'success': True,
            'data': {
                'persons': persons,
                'pagination': {
                    'total_count': total_count,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total_count + per_page - 1) // per_page
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 
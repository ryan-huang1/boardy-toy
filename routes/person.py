from flask import Blueprint, jsonify, request
from database import MongoDB
from datetime import datetime
from embeddings import EmbeddingGenerator
import re

# Create blueprint
person_bp = Blueprint('person', __name__)

# Phone number validation regex
PHONE_REGEX = re.compile(r'^\+[1-9]\d{1,14}$')

def validate_phone_number(phone_number):
    """Validate phone number format using E.164 standard"""
    return bool(PHONE_REGEX.match(phone_number))

@person_bp.route('/create', methods=['POST'])
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
            
        # Get interests and skills
        interests = data.get('interests', [])
        skills = data.get('skills', [])
        
        # Generate embedding for interests and skills
        embedding_generator = EmbeddingGenerator()
        vector_embedding = embedding_generator.generate_combined_embedding(interests, skills)
            
        # Prepare person document
        now = datetime.utcnow()
        person = {
            'phoneNumber': data['phoneNumber'],
            'name': data['name'],
            'interests': interests,
            'skills': skills,
            'bio': data.get('bio', ''),
            'location': data.get('location', ''),
            'vectorEmbedding': vector_embedding,
            'createdAt': now,
            'updatedAt': now
        }
        
        # Insert person into database
        result = db.persons.insert_one(person)
        
        # Remove _id and vectorEmbedding from response
        person.pop('_id', None)
        person.pop('vectorEmbedding', None)
        
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

@person_bp.route('/list', methods=['GET'])
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

@person_bp.route('/delete-all', methods=['DELETE'])
def delete_all_persons():
    try:
        # Get database instance
        db = MongoDB().get_db()
        
        # Delete all documents from persons collection
        result = db.persons.delete_many({})
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {result.deleted_count} persons',
            'data': {
                'deleted_count': result.deleted_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500

@person_bp.route('/<phone_number>', methods=['GET'])
def get_person(phone_number):
    try:
        # Get database instance
        db = MongoDB().get_db()
        
        # Find person by phone number
        person = db.persons.find_one({'phoneNumber': phone_number})
        
        # Return 404 if person not found
        if not person:
            return jsonify({
                'success': False,
                'error': 'Person not found',
                'code': 404
            }), 404
            
        # Remove MongoDB _id and vector embedding from response
        person.pop('_id', None)
        person.pop('vectorEmbedding', None)
        
        return jsonify({
            'success': True,
            'data': person
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500 
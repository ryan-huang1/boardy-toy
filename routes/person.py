from flask import Blueprint, jsonify, request
from database import MongoDB
from datetime import datetime, UTC
from embeddings import EmbeddingGenerator
import re
import numpy as np
import json

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
        embedding_generator = EmbeddingGenerator.get_instance()
        vector_embedding = embedding_generator.generate_combined_embedding(interests, skills)
            
        # Prepare person document
        now = datetime.now(UTC)
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
        per_page = int(request.args.get('per_page', 100))
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 100
            
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        # Get total count of documents
        total_count = db.persons.count_documents({})
        
        # Get paginated results
        cursor = db.persons.find({}).skip(skip).limit(per_page)
        
        # Convert cursor to list and process each document
        persons = []
        for person in cursor:
            # Get the first 5 dimensions of the embedding vector if it exists
            embedding_preview = None
            if person.get('vectorEmbedding') and len(person['vectorEmbedding']) > 0:
                embedding_preview = person['vectorEmbedding'][:5]
            
            # Remove full embedding from response
            person.pop('vectorEmbedding', None)
            person.pop('_id', None)
            
            # Add embedding preview if available
            if embedding_preview is not None:
                person['embeddingPreview'] = embedding_preview
                
            # Get conversation history for this person
            conversations = list(db.conversations.find(
                {'call_uuid': {'$regex': person['phoneNumber']}},
                {'_id': 0, 'messages': 1}
            ))
            
            # Add conversation histories to person object
            person['conversations'] = []
            for conv in conversations:
                if 'messages' in conv:
                    # Format each message for display
                    formatted_messages = []
                    for msg in conv['messages']:
                        formatted_messages.append({
                            'role': msg['role'],
                            'content': msg['content'],
                            'timestamp': msg.get('timestamp', '')
                        })
                    person['conversations'].append(formatted_messages)
            
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

@person_bp.route('', methods=['GET'])
def get_person():
    try:
        # Get phone number from query parameters
        phone_number = request.args.get('phone_number')
        
        # Validate phone number is provided
        if not phone_number:
            return jsonify({
                'success': False,
                'error': 'Phone number is required as a query parameter',
                'code': 400
            }), 400
            
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

@person_bp.route('', methods=['PUT'])
def update_person():
    try:
        # Get phone number from query parameters
        phone_number = request.args.get('phone_number')
        
        # Validate phone number is provided
        if not phone_number:
            return jsonify({
                'success': False,
                'error': 'Phone number is required as a query parameter',
                'code': 400
            }), 400
            
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
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data',
                'code': 400
            }), 400
            
        def normalize_strings(items):
            """Normalize strings by converting to lowercase and stripping whitespace"""
            return [str(item).lower().strip() for item in items]
            
        def remove_duplicates(items):
            """Remove duplicates while preserving original case of first occurrence"""
            seen = {}  # lowercase -> original case
            for item in items:
                norm = str(item).lower().strip()
                if norm not in seen:
                    seen[norm] = item
            return list(seen.values())
            
        # Update fields if provided in request
        update_data = {}
        interests_updated = False
        skills_updated = False
        bio_updated = False
        
        if 'name' in data:
            update_data['name'] = data['name']
        if 'interests' in data:
            # Normalize and combine interests
            current_interests = normalize_strings(person.get('interests', []))
            new_interests = normalize_strings(data['interests'])
            # Use sets for efficient union operation
            combined_normalized = set(current_interests).union(new_interests)
            # Get original case versions
            all_interests = person.get('interests', []) + data['interests']
            update_data['interests'] = remove_duplicates(all_interests)
            interests_updated = True
        if 'skills' in data:
            # Normalize and combine skills
            current_skills = normalize_strings(person.get('skills', []))
            new_skills = normalize_strings(data['skills'])
            # Use sets for efficient union operation
            combined_normalized = set(current_skills).union(new_skills)
            # Get original case versions
            all_skills = person.get('skills', []) + data['skills']
            update_data['skills'] = remove_duplicates(all_skills)
            skills_updated = True
        if 'bio' in data:
            update_data['bio'] = data['bio']
            bio_updated = True
        if 'location' in data:
            update_data['location'] = data['location']
            
        # Update vector embedding if interests, skills, or bio changed
        if interests_updated or skills_updated or bio_updated:
            # Get current or updated values
            interests = update_data.get('interests', person.get('interests', []))
            skills = update_data.get('skills', person.get('skills', []))
            bio = update_data.get('bio', person.get('bio', ''))
            
            # Generate new embedding
            embedding_generator = EmbeddingGenerator.get_instance()
            update_data['vectorEmbedding'] = embedding_generator.generate_combined_embedding(
                interests=interests,
                skills=skills,
                bio=bio
            )
            
        # Update timestamp
        update_data['updatedAt'] = datetime.now(UTC)
        
        # Update person in database
        result = db.persons.update_one(
            {'phoneNumber': phone_number},
            {'$set': update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({
                'success': False,
                'error': 'No changes made to person',
                'code': 400
            }), 400
            
        # Get updated person
        updated_person = db.persons.find_one({'phoneNumber': phone_number})
        
        # Remove _id and vectorEmbedding from response
        updated_person.pop('_id', None)
        updated_person.pop('vectorEmbedding', None)
        
        return jsonify({
            'success': True,
            'message': 'Person updated successfully',
            'data': updated_person
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500

@person_bp.route('/similar', methods=['GET'])
def find_similar_people():
    try:
        timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{timestamp}] === Similar People Search Request ===")
        print(f"[{timestamp}] Query Parameters: {dict(request.args)}")
        print(f"[{timestamp}] Headers: {dict(request.headers)}")
        print(f"[{timestamp}] Remote Address: {request.remote_addr}")
        print(f"[{timestamp}] ===================================\n")

        # Get and validate query parameter
        query_text = request.args.get('query')
        
        # Validate query is present and is a string
        if not isinstance(query_text, str):
            print(f"[{timestamp}] Error: Query must be a string, got {type(query_text)}")
            return jsonify({
                'success': False,
                'error': 'Query must be a string',
                'code': 400
            }), 400
            
        # Validate query is not empty after stripping whitespace
        query_text = query_text.strip()
        if not query_text:
            print(f"[{timestamp}] Error: Empty query after stripping whitespace")
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty',
                'code': 400
            }), 400
            
        print(f"[{timestamp}] Processing search query: '{query_text}'")
            
        # Get database instance
        db = MongoDB().get_db()
        
        # Generate embedding for the query text
        embedding_generator = EmbeddingGenerator.get_instance()
        query_embedding = embedding_generator.generate_embedding(query_text)
        
        if not query_embedding:
            print(f"[{timestamp}] Error: Could not generate embedding for query")
            return jsonify({
                'success': False,
                'error': 'Could not generate embedding for query',
                'code': 400
            }), 400
            
        # Get all candidates
        candidates = list(db.persons.find({
            'vectorEmbedding': {'$exists': True, '$ne': None}
        }))
        print(f"[{timestamp}] Found {len(candidates)} candidates with embeddings")
        
        # Calculate cosine similarity for each candidate
        results = []
        query_norm = np.linalg.norm(query_embedding)
        
        for candidate in candidates:
            candidate_embedding = candidate['vectorEmbedding']
            candidate_norm = np.linalg.norm(candidate_embedding)
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, candidate_embedding) / (query_norm * candidate_norm)
            
            if similarity > 0:
                results.append({
                    'phoneNumber': candidate['phoneNumber'],
                    'name': candidate['name'],
                    'interests': candidate.get('interests', []),
                    'skills': candidate.get('skills', []),
                    'bio': candidate.get('bio', ''),
                    'location': candidate.get('location', ''),
                    'similarity': float(similarity)
                })
        
        print(f"[{timestamp}] Found {len(results)} candidates with positive similarity")
        
        # Sort by similarity and get only the best match
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        if not results:
            print(f"[{timestamp}] No matches found")
            return jsonify({
                'success': True,
                'best_match': None,
                'found': False
            })
            
        best_match = results[0]
        print(f"[{timestamp}] Best match: {best_match['name']} with similarity {best_match['similarity']:.3f}")
        
        # Format response for easy extraction by Bland AI
        response = {
            'success': True,
            'found': True,
            'best_match': {
                'phone': best_match['phoneNumber'],  # Simplified key name
                'name': best_match['name'],
                'interests': ', '.join(best_match['interests']),  # Join lists for easier extraction
                'skills': ', '.join(best_match['skills']),
                'bio': best_match['bio'],
                'location': best_match['location'],
                'match_score': round(best_match['similarity'] * 100, 1)  # Convert to percentage
            }
        }
        print(f"[{timestamp}] Returning response: {json.dumps(response, indent=2)}")
        return jsonify(response)
        
    except Exception as e:
        timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Error in find_similar_people: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500

@person_bp.route('/delete-conversations', methods=['DELETE'])
def delete_all_conversations():
    try:
        # Get database instance
        db = MongoDB().get_db()
        
        # Delete all documents from conversations collection
        result = db.conversations.delete_many({})
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {result.deleted_count} conversations',
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
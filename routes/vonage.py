from flask import Blueprint, Response, send_from_directory, request, jsonify
import json
import os
from vonage import Vonage, Auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create blueprint
vonage_bp = Blueprint('vonage', __name__)

# Get the absolute path of the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define server URL
SERVER_URL = "https://dolphin-app-bsmq7.ondigitalocean.app"

# Environment Variables for Vonage
VONAGE_APPLICATION_ID = os.getenv('VONAGE_APPLICATION_ID')
API_KEY_PATH = os.getenv('API_KEY_PATH')
VONAGE_NUMBER = os.getenv('VONAGE_NUMBER')

# Vonage Client Setup
client = Vonage(
    auth=Auth(
        application_id=VONAGE_APPLICATION_ID,
        private_key=API_KEY_PATH,
    )
)

@vonage_bp.route('/intro-audio')
def serve_intro_audio():
    """Serve the intro.mp3 file"""
    return send_from_directory(BASE_DIR, 'intro.mp3')

@vonage_bp.route('/webhooks/inbound', methods=['GET'])
def handle_inbound_call():
    """Handle inbound calls from Vonage"""
    print("Received inbound call")
    
    # Create NCCO to play intro.mp3
    ncco = [{
        'action': 'stream',
        'streamUrl': [f"{SERVER_URL}/api/vonage/intro-audio"],
        'bargeIn': True
    }]
    
    return Response(json.dumps(ncco), mimetype='application/json')

@vonage_bp.route('/webhooks/event', methods=['POST'])
def handle_event():
    """Handle Vonage events"""
    print("Event received:", request.json)
    return "OK", 200

@vonage_bp.route('/make-call', methods=['GET'])
def make_call():
    """Make an outbound call"""
    if not request.args.get('to_number'):
        return jsonify({
            'error': 'Missing to_number parameter'
        }), 400
        
    to_number = request.args.get('to_number')
    
    response = client.voice.create_call({
        'to': [{
            'type': 'phone',
            'number': to_number
        }],
        'from': {
            'type': 'phone',
            'number': VONAGE_NUMBER
        },
        'answer_url': [f"{SERVER_URL}/api/vonage/webhooks/inbound"]
    })
    
    uuid = response['uuid']
    print(f"Call initiated with UUID: {uuid}")
    return jsonify({
        'success': True,
        'uuid': uuid,
        'message': 'Call initiated successfully'
    }) 
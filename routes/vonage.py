from flask import Blueprint, Response, send_from_directory, request, jsonify
import json
import os
from vonage import Vonage, Auth
from dotenv import load_dotenv
from datetime import datetime

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
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Serving intro audio file from {BASE_DIR}")
    return send_from_directory(BASE_DIR, 'intro.mp3')

@vonage_bp.route('/webhooks/inbound', methods=['GET'])
def handle_inbound_call():
    """Handle inbound calls from Vonage"""
    call_uuid = request.args.get('uuid', 'No UUID provided')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received inbound call - UUID: {call_uuid}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Call parameters: {request.args}")
    
    # Create NCCO with both stream and input actions
    ncco = [{
        'action': 'stream',
        'streamUrl': [f"{SERVER_URL}/api/vonage/intro-audio"],
        'bargeIn': True
    }, {
        'action': 'input',
        'eventUrl': [f"{SERVER_URL}/api/vonage/webhooks/input"],
        'type': ['speech'],
        'speech': {
            'uuid': [request.args.get('uuid')],
            'endOnSilence': 1,
            'sensitivity': '10',
            'language': 'en-US'
        }
    }]
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Returning NCCO for call {call_uuid}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NCCO content: {json.dumps(ncco, indent=2)}")
    return Response(json.dumps(ncco), mimetype='application/json')

@vonage_bp.route('/webhooks/input', methods=['POST'])
def handle_input():
    """Handle speech input from the call"""
    try:
        input_data = request.json
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Speech input received")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Input data: {json.dumps(input_data, indent=2)}")
        
        # Print specific speech results if available
        if input_data.get('speech') and input_data['speech'].get('results'):
            for result in input_data['speech']['results']:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Speech text: {result.get('text', 'No text')} - Confidence: {result.get('confidence', 'N/A')}")
        
        return "OK", 200
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Error processing speech input: {str(e)}")
        return "Error", 500

@vonage_bp.route('/webhooks/event', methods=['POST'])
def handle_event():
    """Handle Vonage events"""
    try:
        event_data = request.json
        event_type = event_data.get('type', 'unknown')
        call_uuid = event_data.get('uuid', 'No UUID')
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received event type: {event_type} for call: {call_uuid}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Full event data: {json.dumps(event_data, indent=2)}")
        
        return "OK", 200
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Error processing event: {str(e)}")
        return "Error", 500
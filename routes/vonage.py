from flask import Blueprint, Response, send_from_directory, request, jsonify
import json
import os
import uuid
from vonage import Vonage, Auth
from dotenv import load_dotenv
from datetime import datetime
from llm import LLMGeneration
from voice import Voice
from database import MongoDB

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

# Create audio directory if it doesn't exist
AUDIO_DIR = os.path.join(BASE_DIR, 'generated_audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

# Initialize LLM and Voice instances
llm_generator = LLMGeneration()
voice_generator = Voice()

def generate_audio_filename():
    """Generate a unique filename for audio files"""
    return f"{uuid.uuid4()}.mp3"

def cleanup_old_audio_files():
    """Clean up audio files older than 1 hour"""
    try:
        current_time = datetime.now().timestamp()
        for filename in os.listdir(AUDIO_DIR):
            filepath = os.path.join(AUDIO_DIR, filename)
            if os.path.getctime(filepath) < current_time - 3600:  # 1 hour
                os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up audio files: {e}")

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
    
    # Store initial greeting in MongoDB
    initial_greeting = "Hey I'm Boardy, it's nice to meet you. Who am I speaking with?"
    db = MongoDB()
    db.update_conversation(call_uuid, assistant_message=initial_greeting)
    
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
            'uuid': [call_uuid],
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
        call_uuid = input_data.get('uuid', '')  # Get call UUID
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Speech input received for call: {call_uuid}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Input data: {json.dumps(input_data, indent=2)}")
        
        # Extract speech text from results
        speech_text = ""
        if input_data.get('speech') and input_data['speech'].get('results'):
            result = input_data['speech']['results'][0]  # Get first result
            speech_text = result.get('text', '')
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Speech text: {speech_text}")

        # Clean up old audio files
        cleanup_old_audio_files()

        # Get conversation history from MongoDB
        db = MongoDB()
        conversation_history = db.get_conversation_history(call_uuid)
        
        # Build messages list with system prompt and conversation history
        messages = [
            {"role": "system", "content": llm_generator.get_system_prompt()},
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": speech_text})
        
        # Generate LLM response
        llm_response = "".join(list(llm_generator.generate_response(messages)))
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] LLM response: {llm_response}")

        # Update conversation history with new messages
        db.update_conversation(
            call_uuid,
            user_message=speech_text,
            assistant_message=llm_response
        )

        # Generate audio from LLM response
        audio_filename = generate_audio_filename()
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        voice_generator.generate_speech(llm_response, output_path=audio_path)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generated audio: {audio_filename}")

        # Create NCCO response
        ncco = [{
            'action': 'stream',
            'streamUrl': [f"{SERVER_URL}/api/vonage/audio/{audio_filename}"],
            'bargeIn': True
        }, {
            'action': 'input',
            'eventUrl': [f"{SERVER_URL}/api/vonage/webhooks/input"],
            'type': ['speech'],
            'speech': {
                'uuid': [call_uuid],
                'endOnSilence': 1,
                'sensitivity': '10',
                'language': 'en-US'
            }
        }]

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Returning NCCO: {json.dumps(ncco, indent=2)}")
        return Response(json.dumps(ncco), mimetype='application/json')

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

@vonage_bp.route('/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        return send_from_directory(AUDIO_DIR, filename)
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Error serving audio file: {str(e)}")
        return "Error", 500
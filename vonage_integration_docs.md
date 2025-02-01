# Vonage Integration and Voice API Functionality Documentation

## Overview of Vonage Integration in the Project

1. **Vonage Client Initialization:**

   - The project uses the Vonage Python SDK to interact with Vonage's Voice API.
   - The client is initialized using credentials loaded from environment variables (e.g., `VONAGE_APPLICATION_ID` and `API_KEY_PATH`). These credentials allow the app to authenticate and send voice call commands.

2. **Initiating a Call (`/make-call` endpoint):**

   - The endpoint `/make-call` creates an outbound call to a predefined phone number (specified by the environment variable `TO_NUMBER`).
   - The `client.voice.create_call` method is used to initiate the call. The payload includes the `to` and `from` numbers, and an `answer_url`—a webhook endpoint (in this case, `/webhooks/answer`) that Vonage will request when the call is answered.
   - The call response returns a unique identifier (`uuid`), which is then printed and returned to the caller.

3. **Handling the Answer Webhook (`/webhooks/answer` endpoint):**

   - When the call is answered by the recipient, Vonage makes a GET request to `/webhooks/answer`.
   - This endpoint returns an NCCO (Nexmo Call Control Object) in JSON format. The NCCO instructs Vonage on how to handle the call.
     - **Stream Action:**
       - Plays a pre-generated audio message.
       - The audio file is served via another endpoint (`/hello-audio/<filename>`).
     - **Input Action:**
       - Listens for user speech. The NCCO includes a speech input configuration that specifies details such as the language (`en-US`), sensitivity, and a reference to the `uuid` (passed along in the query parameters).
   - **NCCO Structure:**
     - The returned NCCO array contains two actions:
       1. **Stream Action:** Plays the audio.
       2. **Input Action:** Waits for and captures the speech input, posting results back to another webhook (`/webhooks/input`).

4. **Handling Speech Input (`/webhooks/input` endpoint):**

   - When the user speaks, Vonage sends a POST request to `/webhooks/input` with the recognized speech data.
   - The endpoint extracts the UUID and the speech results.
   - The endpoint processes the speech results and can respond with a new NCCO to continue the conversation.

5. **Additional Webhook (`/webhooks/event`):**
   - This endpoint is used for receiving other events (such as call status updates) from Vonage. It currently logs the event data and responds with a simple acknowledgment.

## Comprehensive Documentation on Vonage Voice Functionality

### 1. Vonage Voice API Basics

- **Voice Calls and NCCOs:**  
  Vonage Voice API uses NCCOs (Nexmo Call Control Objects) to control the flow of a call. An NCCO is a JSON array of actions that tells Vonage how to manage the call. Common actions include:

  - **`talk`**: Convert text to speech using Vonage's built-in TTS.
  - **`stream`**: Play an audio file or stream to the call.
  - **`input`**: Capture user input (DTMF tones or speech) during the call.
  - **`record`**: Record the call.
  - **`notify`**: Send events or notifications to a URL.

- **Call Lifecycle:**
  1. **Call Initiation:** Your server instructs Vonage to start a call.
  2. **Answer Webhook:** When the call is answered, Vonage requests the `answer_url` which should return an NCCO.
  3. **Ongoing Interaction:** The NCCO directs the call's behavior—playing audio, collecting input, etc.
  4. **Event Webhooks:** Vonage may send events (like call status changes) to an `event_url` to inform your application of updates.

## Summary

In this project, Vonage is used to:

- **Initiate Outbound Calls:**  
  The `/make-call` endpoint creates a call from your server to a specified phone number.

- **Control the Call Flow:**  
  Once the call is answered, an NCCO (provided by the `/webhooks/answer` endpoint) instructs Vonage to play an audio message (using the stream action) and capture the caller's speech (using the input action).

- **Process Speech Input:**  
  The `/webhooks/input` endpoint handles the incoming speech data and returns a new NCCO to continue the conversation.

- **Manage Events:**  
  The `/webhooks/event` endpoint logs additional call events for monitoring and debugging.

This design leverages Vonage's real-time voice capabilities to build an interactive voice application.

## Code Examples

### 1. Initializing the Vonage Client

```python
import vonage
import os
from dotenv import load_dotenv

load_dotenv()
VONAGE_APPLICATION_ID = os.getenv('VONAGE_APPLICATION_ID')
API_KEY_PATH = os.getenv('API_KEY_PATH')

client = vonage.Client(
    application_id=VONAGE_APPLICATION_ID,
    private_key=API_KEY_PATH,
)
```

### 2. Making a Call

```python
@app.route('/make-call', methods=['GET'])
def make_call():
    response = client.voice.create_call({
        'to': [{
            'type': 'phone',
            'number': TO_NUMBER
        }],
        'from': {
            'type': 'phone',
            'number': VONAGE_NUMBER
        },
        'answer_url': [f"{server_remote_url}webhooks/answer"]
    })
    uuid = response['uuid']
    print(uuid)
    return f"Call initiated with UUID: {uuid}", 200
```

### 3. Handling Incoming Calls (Answer Webhook)

```python
@app.route('/webhooks/answer', methods=['GET'])
def answer_call():
    text_to_convert = "Hello? Is that you calling? I'm so happy to hear from you!"
    audio_filename = generate_audio_file(text_to_convert, AUDIO_FILE_PATH)
    audio_url = f"{server_remote_url}hello-audio/{audio_filename}"

    ncco = [{
        'action': 'stream',
        "streamUrl": [audio_url],
        "bargeIn": "true"
    }, {
        'action': 'input',
        'eventUrl': [f"{server_remote_url}webhooks/input"],
        'type': ['speech'],
        'speech': {
            'uuid': [request.args.get('uuid')],
            'endOnSilence': 1,
            'sensitivity': '10',
            'language': 'en-US'
        }
    }]
    return Response(json.dumps(ncco), mimetype='application/json')
```

### 4. Handling User Speech Input

```python
@app.route('/webhooks/input', methods=['POST'])
def handle_input():
    input_data = request.json
    uuid = input_data.get('uuid', 'No UUID found')
    speech_results = input_data.get('speech', {}).get('results', [])

    if speech_results:
        highest_confidence_result = max(
            speech_results, key=lambda result: result.get('confidence', 0))
        user_text = highest_confidence_result.get('text', '')
    else:
        user_text = "Call ended"

    # Generate your response text here
    response_text = "Thank you for your message!"

    # Generate audio for the response
    audio_filename = generate_audio_file(response_text, AUDIO_FILE_PATH)
    audio_url = f"{server_remote_url}hello-audio/{audio_filename}"

    response_ncco = [{
        'action': 'stream',
        "streamUrl": [audio_url],
        "bargeIn": "true"
    }, {
        'action': 'input',
        'eventUrl': [f"{server_remote_url}webhooks/input"],
        'type': ['speech'],
        'speech': {
            'uuid': [request.json['uuid']],
            'endOnSilence': 1,
            'sensitivity': '10',
            'language': 'en-US'
        }
    }]
    return jsonify(response_ncco)
```

### 5. Serving Audio Files

```python
@app.route('/hello-audio/<filename>')
def serve_audio(filename):
    """Serve the dynamically generated MP3 audio file."""
    return send_from_directory(AUDIO_FILE_PATH, filename)
```

from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
from dotenv import load_dotenv
import os
import uuid
import io
from pydub import AudioSegment  # For audio format conversion

# Load environment variables from .env file
load_dotenv()

# Access environment variables
api_key = os.getenv('11LABS_API_KEY')

# Initialize the ElevenLabs client
client = ElevenLabs(api_key=api_key)


def generate_audio_file(text, directory='audio_files'):
    """
    Generates an MP3 audio file from the provided text using ElevenLabs API and saves it in the specified directory.
    
    Args:
    text (str): The text to be converted to speech.
    directory (str): The directory where the audio file will be saved.
    
    Returns:
    str: The filename of the saved audio file.
    """
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate a random UUID for the filename
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(directory, filename)

    # Generate the audio content
    audio_generator = client.generate(
        model="eleven_turbo_v2_5",
        text=text,
        voice=Voice(voice_id='eVItLK1UvXctxuaRV2Oq',
                    settings=VoiceSettings(stability=0.71,
                                           similarity_boost=0.5,
                                           style=0.0,
                                           use_speaker_boost=True)))

    # Collect all audio data into a byte array
    audio_data = bytes()
    for chunk in audio_generator:
        audio_data += chunk

    # Load the audio data into AudioSegment and export it as MP3
    try:
        sound = AudioSegment.from_raw(io.BytesIO(audio_data),
                                      sample_width=2,
                                      frame_rate=24000,
                                      channels=1)
        sound.export(filepath, format="mp3")
    except Exception as e:
        print(f"Failed to process audio data: {e}")

    return filename


# Example usage
text_to_convert = '''In the heart of an ancient forest, a curious phenomenon occurs each year on the eve of the autumn equinox.'''
# audio_filename = generate_audio_file(text_to_convert)
# print(f"Audio file saved as {audio_filename}")

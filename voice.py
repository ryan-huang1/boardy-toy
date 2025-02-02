import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Voice:
    """A class to handle text-to-speech generation using ElevenLabs API"""
    
    # Base URL for ElevenLabs API
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    def __init__(self):
        """Initialize the Voice class with API key from environment variables"""
        self.api_key = os.getenv('ELEVEN_LABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVEN_LABS_API_KEY environment variable is not set")
            
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

    def generate_speech(self, text, voice_id="pqHfZKP75CvOlQylNhV4", output_path=None):
        """
        Generate speech using ElevenLabs API
        
        Args:
            text (str): The text to convert to speech
            voice_id (str): The ID of the voice to use
            output_path (str, optional): Path to save the audio file
            
        Returns:
            bytes or str: Audio bytes or file path
        """
        try:
            url = f"{self.BASE_URL}/text-to-speech/{voice_id}"
            
            data = {
                "text": text,
                "model_id": "eleven_flash_v2_5",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                return response.content
                
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise 
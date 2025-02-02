import os
import requests
import io
from dotenv import load_dotenv
from pydub import AudioSegment

# Load environment variables
load_dotenv()

class Voice:
    """A class to handle text-to-speech generation using ElevenLabs API"""
    
    # Base URL for ElevenLabs API
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Chunk size for streaming audio
    CHUNK_SIZE = 1024
    
    # Enhanced telephony audio settings for better clarity
    SAMPLE_RATE = 16000  # 16kHz for better voice quality
    CHANNELS = 1         # Mono
    BITS = 16           # 16-bit depth for better dynamic range
    
    def __init__(self):
        """Initialize the Voice class with API key from environment variables"""
        self.api_key = os.getenv('ELEVEN_LABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVEN_LABS_API_KEY environment variable is not set")
            
        # Common headers for API requests
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

    def _downsample_audio(self, audio_bytes):
        """
        Process audio for telephony while maintaining clarity (16kHz, mono, 16-bit)
        
        Args:
            audio_bytes (bytes): Original audio in bytes
            
        Returns:
            bytes: Processed audio in bytes
        """
        # Load audio from bytes
        audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        
        # Convert to mono if stereo
        if audio.channels > 1:
            audio = audio.set_channels(self.CHANNELS)
        
        # Set sample rate to 16kHz
        audio = audio.set_frame_rate(self.SAMPLE_RATE)
        
        # Set to 16-bit depth
        audio = audio.set_sample_width(self.BITS // 8)
        
        # Normalize audio to maximize volume while preventing clipping
        audio = audio.normalize()
        
        # Apply mild compression to enhance clarity
        audio = audio.compress_dynamic_range()
        
        # Export to bytes with a higher bitrate for better quality
        buffer = io.BytesIO()
        audio.export(buffer, format='mp3', bitrate='64k')
        return buffer.getvalue()

    def generate_speech(self, text, voice_id="pqHfZKP75CvOlQylNhV4", output_path=None):
        """
        Generate speech from text using ElevenLabs API and downsample for telephony
        
        Args:
            text (str): The text to convert to speech
            voice_id (str): The ID of the voice to use (default is specified voice)
            output_path (str, optional): Path to save the audio file. If None, returns the audio bytes
            
        Returns:
            bytes or str: If output_path is None, returns the downsampled audio bytes.
                         If output_path is provided, returns the path to the saved file.
        """
        try:
            # API endpoint for text-to-speech
            url = f"{self.BASE_URL}/text-to-speech/{voice_id}"
            
            # Request payload with optimized voice settings
            data = {
                "text": text,
                "model_id": "eleven_turbo_v2_5",  # Using Turbo v2.5 model
                "voice_settings": {
                    "stability": 0.3,         # Lowered for more expressive output
                    "similarity_boost": 0.8,   # Increased for better voice matching
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            # Make the API request
            response = requests.post(url, json=data, headers=self.headers)
            
            # Check if request was successful
            response.raise_for_status()
            
            # Get audio content
            audio_content = response.content
            
            # Downsample the audio
            downsampled_audio = self._downsample_audio(audio_content)
            
            # If output path is provided, save the downsampled audio file
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(downsampled_audio)
                return output_path
            
            # Otherwise return the downsampled audio bytes
            return downsampled_audio
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error generating speech: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing audio: {str(e)}") 
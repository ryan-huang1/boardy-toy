import os
import requests
import io
import time
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
        start_time = time.time()
        
        # Load audio from bytes
        print(f"Starting audio loading...")
        audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        print(f"Audio loading completed in {time.time() - start_time:.2f} seconds")
        
        # Convert to mono if stereo
        if audio.channels > 1:
            mono_start = time.time()
            audio = audio.set_channels(self.CHANNELS)
            print(f"Conversion to mono completed in {time.time() - mono_start:.2f} seconds")
        
        # Set sample rate to 16kHz
        sample_rate_start = time.time()
        audio = audio.set_frame_rate(self.SAMPLE_RATE)
        print(f"Sample rate adjustment completed in {time.time() - sample_rate_start:.2f} seconds")
        
        # Set to 16-bit depth
        bit_depth_start = time.time()
        audio = audio.set_sample_width(self.BITS // 8)
        print(f"Bit depth adjustment completed in {time.time() - bit_depth_start:.2f} seconds")
        
        # Normalize audio
        normalize_start = time.time()
        audio = audio.normalize()
        print(f"Audio normalization completed in {time.time() - normalize_start:.2f} seconds")
        
        # Apply compression
        compress_start = time.time()
        audio = audio.compress_dynamic_range()
        print(f"Audio compression completed in {time.time() - compress_start:.2f} seconds")
        
        # Export to bytes
        export_start = time.time()
        buffer = io.BytesIO()
        audio.export(buffer, format='mp3', bitrate='64k')
        print(f"Audio export completed in {time.time() - export_start:.2f} seconds")
        
        total_time = time.time() - start_time
        print(f"Total audio processing time: {total_time:.2f} seconds")
        
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
        start_time = time.time()
        
        try:
            # API endpoint for text-to-speech
            url = f"{self.BASE_URL}/text-to-speech/{voice_id}"
            
            # Request payload with optimized voice settings
            data = {
                "text": text,
                "model_id": "eleven_flash_v2_5",  # Using Turbo v2.5 model
                "voice_settings": {
                    "stability": 0.3,         # Lowered for more expressive output
                    "similarity_boost": 0.8,   # Increased for better voice matching
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            # Make the API request
            print(f"Starting API request to ElevenLabs...")
            api_start = time.time()
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            print(f"API request completed in {time.time() - api_start:.2f} seconds")
            
            # Get audio content
            audio_content = response.content
            
            # Downsample the audio
            print("Starting audio downsampling...")
            downsample_start = time.time()
            downsampled_audio = self._downsample_audio(audio_content)
            print(f"Audio downsampling completed in {time.time() - downsample_start:.2f} seconds")
            
            # Save if output path provided
            if output_path:
                save_start = time.time()
                with open(output_path, 'wb') as f:
                    f.write(downsampled_audio)
                print(f"File saving completed in {time.time() - save_start:.2f} seconds")
                result = output_path
            else:
                result = downsampled_audio
            
            total_time = time.time() - start_time
            print(f"Total speech generation time: {total_time:.2f} seconds")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed after {time.time() - start_time:.2f} seconds")
            raise Exception(f"Error generating speech: {str(e)}")
        except Exception as e:
            print(f"Processing failed after {time.time() - start_time:.2f} seconds")
            raise Exception(f"Error processing audio: {str(e)}") 
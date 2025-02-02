import os
import requests
import io
import time
from dotenv import load_dotenv
from pydub import AudioSegment
from functools import lru_cache

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
    
    def __init__(self, enable_compression=False):
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
        
        self.enable_compression = enable_compression
        # Initialize cache for processed audio segments
        self._audio_segment_cache = {}

    @lru_cache(maxsize=32)
    def _get_cached_audio_segment(self, audio_bytes_hash):
        """Cache processed AudioSegment objects to avoid redundant processing"""
        return AudioSegment.from_mp3(io.BytesIO(audio_bytes))

    def _downsample_audio(self, audio_bytes):
        """
        Process audio for telephony while maintaining clarity (16kHz, mono, 16-bit)
        
        Args:
            audio_bytes (bytes): Original audio in bytes
            
        Returns:
            bytes: Processed audio in bytes
        """
        start_time = time.time()
        
        # Load audio from bytes using optimized loading
        print(f"Starting audio loading...")
        try:
            # Try to use cached version first
            audio_bytes_hash = hash(audio_bytes)
            if audio_bytes_hash in self._audio_segment_cache:
                audio = self._audio_segment_cache[audio_bytes_hash]
            else:
                audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
                self._audio_segment_cache[audio_bytes_hash] = audio
        except Exception:
            # Fallback to regular loading if caching fails
            audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        
        print(f"Audio loading completed in {time.time() - start_time:.2f} seconds")
        
        # Batch process audio modifications for better performance
        processing_start = time.time()
        
        # Convert to mono and adjust sample rate in one pass if possible
        if audio.channels > 1 or audio.frame_rate != self.SAMPLE_RATE:
            audio = audio.set_channels(self.CHANNELS).set_frame_rate(self.SAMPLE_RATE)
        
        # Set bit depth
        audio = audio.set_sample_width(self.BITS // 8)
        
        # Normalize audio (essential for voice clarity)
        audio = audio.normalize()
        
        print(f"Basic audio processing completed in {time.time() - processing_start:.2f} seconds")
        
        # Apply compression only if enabled
        if self.enable_compression:
            compress_start = time.time()
            audio = audio.compress_dynamic_range()
            print(f"Audio compression completed in {time.time() - compress_start:.2f} seconds")
        
        # Export to bytes with optimized settings
        export_start = time.time()
        buffer = io.BytesIO()
        
        # Use optimized export parameters
        export_params = {
            'format': 'mp3',
            'bitrate': '64k',
            'codec': 'libmp3lame',
            'parameters': ['-q:a', '2']  # Better quality-speed trade-off
        }
        
        audio.export(buffer, **export_params)
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
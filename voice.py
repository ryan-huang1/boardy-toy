import os
import requests
import io
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pydub import AudioSegment
from functools import lru_cache

# Load environment variables
load_dotenv()

class Voice:
    """A class to handle text-to-speech generation using ElevenLabs API"""
    
    # Base URL for ElevenLabs API
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Telephony-optimized settings
    SAMPLE_RATE = 8000    # 8kHz for phone calls (standard telephony)
    CHANNELS = 1          # Mono
    BITS = 16            # 16-bit depth
    MAX_WORKERS = 4      # Maximum number of threads for parallel processing
    
    def __init__(self, optimize_for_telephony=True):
        """Initialize the Voice class with API key from environment variables"""
        self.api_key = os.getenv('ELEVEN_LABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVEN_LABS_API_KEY environment variable is not set")
            
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        self.optimize_for_telephony = optimize_for_telephony
        self._audio_segment_cache = {}
        self._cache_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)

    @lru_cache(maxsize=32)
    def _get_cached_audio_segment(self, audio_bytes_hash):
        """Cache processed AudioSegment objects to avoid redundant processing"""
        return AudioSegment.from_mp3(io.BytesIO(audio_bytes))

    def _process_audio_segment(self, audio):
        """Process a single audio segment with telephony optimizations"""
        if audio.channels > 1:
            audio = audio.set_channels(self.CHANNELS)
        if audio.frame_rate != self.SAMPLE_RATE:
            audio = audio.set_frame_rate(self.SAMPLE_RATE)
        if audio.sample_width != self.BITS // 8:
            audio = audio.set_sample_width(self.BITS // 8)
        return audio

    def _downsample_audio(self, audio_bytes):
        """
        Optimized audio processing for telephony
        
        Args:
            audio_bytes (bytes): Original audio in bytes
            
        Returns:
            bytes: Processed audio optimized for telephony
        """
        start_time = time.time()
        
        # Fast path: Check cache first
        audio_bytes_hash = hash(audio_bytes)
        with self._cache_lock:
            if audio_bytes_hash in self._audio_segment_cache:
                print("Cache hit! Using cached audio segment")
                audio = self._audio_segment_cache[audio_bytes_hash]
            else:
                print("Cache miss. Loading and processing audio...")
                # Load audio in a separate thread
                future = self._executor.submit(AudioSegment.from_mp3, io.BytesIO(audio_bytes))
                audio = future.result()
                
                # Process audio for telephony
                audio = self._process_audio_segment(audio)
                
                # Cache the processed audio
                self._audio_segment_cache[audio_bytes_hash] = audio
        
        print(f"Audio processing completed in {time.time() - start_time:.2f} seconds")
        
        # Export with telephony-optimized settings
        export_start = time.time()
        buffer = io.BytesIO()
        
        export_params = {
            'format': 'mp3',
            'bitrate': '32k',  # Lower bitrate for telephony
            'codec': 'libmp3lame',
            'parameters': [
                '-q:a', '5',  # Faster encoding, suitable for voice
                '-ac', '1',   # Force mono
                '-ar', str(self.SAMPLE_RATE),  # Force sample rate
            ]
        }
        
        audio.export(buffer, **export_params)
        print(f"Audio export completed in {time.time() - export_start:.2f} seconds")
        
        return buffer.getvalue()

    def generate_speech(self, text, voice_id="pqHfZKP75CvOlQylNhV4", output_path=None):
        """
        Generate speech optimized for telephony
        
        Args:
            text (str): The text to convert to speech
            voice_id (str): The ID of the voice to use
            output_path (str, optional): Path to save the audio file
            
        Returns:
            bytes or str: Audio bytes or file path
        """
        start_time = time.time()
        
        try:
            url = f"{self.BASE_URL}/text-to-speech/{voice_id}"
            
            # Optimized voice settings for telephony
            data = {
                "text": text,
                "model_id": "eleven_flash_v2_5",
                "voice_settings": {
                    "stability": 0.5,         # Balanced for telephony
                    "similarity_boost": 0.75,  # Slightly reduced for faster processing
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            print("Starting API request...")
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            print(f"API request completed in {time.time() - start_time:.2f} seconds")
            
            # Process audio in parallel with other operations
            audio_content = response.content
            future = self._executor.submit(self._downsample_audio, audio_content)
            downsampled_audio = future.result()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(downsampled_audio)
                result = output_path
            else:
                result = downsampled_audio
            
            print(f"Total processing time: {time.time() - start_time:.2f} seconds")
            return result
            
        except Exception as e:
            print(f"Error occurred after {time.time() - start_time:.2f} seconds: {str(e)}")
            raise 
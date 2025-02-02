from voice import Voice
import os

def main():
    # Initialize the Voice class
    voice = Voice()
    
    print("=== ElevenLabs Voice Test Script ===\n")
    
    # Generate speech and save to file
    print("Generating speech and saving to file...")
    test_text = "Hello! This is a test of the ElevenLabs text to speech system using the Turbo v2.5 model."
    try:
        output_path = "test_output.mp3"
        result = voice.generate_speech(
            text=test_text,
            output_path=output_path
        )
        print(f"Audio saved to: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Error generating speech: {e}")

if __name__ == "__main__":
    main() 
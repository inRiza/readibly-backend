import pyttsx3
import os
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TextToSpeech:
    def __init__(self):
        try:
            # Try to initialize pyttsx3
            self.engine = pyttsx3.init()
            self.engine_initialized = True
            logger.info("Text-to-speech engine initialized successfully")
        except Exception as e:
            # Handle initialization failure gracefully
            self.engine = None
            self.engine_initialized = False
            logger.warning(f"Could not initialize text-to-speech engine: {str(e)}. Will return placeholder responses.")
        
        self.audio_dir = "static/audio"
        os.makedirs(self.audio_dir, exist_ok=True)

    def convert_to_speech(self, text: str) -> str:
        """
        Convert text to speech and save as audio file
        Returns the path to the generated audio file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"tts_{timestamp}_{unique_id}.mp3"
        filepath = os.path.join(self.audio_dir, filename)
        
        try:
            if not self.engine_initialized:
                logger.warning("Text-to-speech engine not available. Returning placeholder.")
                # Create an empty file as placeholder
                with open(filepath, 'wb') as f:
                    f.write(b'')  # Write empty file as placeholder
                return filepath
                
            # Configure voice properties
            self.engine.setProperty('rate', 150)    # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level

            # Convert text to speech and save to file
            self.engine.save_to_file(text, filepath)
            self.engine.runAndWait()

            return filepath

        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            # Create an empty file as fallback
            with open(filepath, 'wb') as f:
                f.write(b'')  # Write empty file
            return filepath

    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old audio files
        """
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.audio_dir):
                filepath = os.path.join(self.audio_dir, filename)
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                age_hours = (current_time - file_modified).total_seconds() / 3600

                if age_hours > max_age_hours:
                    os.remove(filepath)

        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
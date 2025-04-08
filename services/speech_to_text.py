import speech_recognition as sr
from fastapi import UploadFile, HTTPException
import io
import wave
import numpy as np
import logging
import subprocess
import os
import shutil
import tempfile

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ffmpeg", "bin", "ffmpeg.exe")
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Check if ffmpeg is installed and accessible."""
        if not os.path.exists(self.ffmpeg_path):
            logger.error(f"FFmpeg not found at {self.ffmpeg_path}")
            raise RuntimeError(
                "FFmpeg is not found in the project directory. Please ensure ffmpeg is installed in the backend/ffmpeg/bin directory."
            )

    async def convert_audio_to_text(self, audio_file: UploadFile) -> str:
        temp_dir = None
        try:
            # Read the audio file
            audio_data = await audio_file.read()
            logger.info(f"Read audio data: {len(audio_data)} bytes")
            
            # Create a temporary directory for processing
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Created temporary directory: {temp_dir}")
            
            # Create a temporary file for the input audio
            input_path = os.path.join(temp_dir, "temp_input.webm")
            with open(input_path, "wb") as f:
                f.write(audio_data)
            
            # Convert WebM to WAV using ffmpeg
            output_path = os.path.join(temp_dir, "temp_output.wav")
            logger.info("Converting audio format using ffmpeg...")
            
            try:
                result = subprocess.run([
                    self.ffmpeg_path, "-i", input_path,
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    "-y",  # Overwrite output file if it exists
                    output_path
                ], check=True, capture_output=True, text=True)
                logger.info("FFmpeg conversion successful")
            except subprocess.CalledProcessError as e:
                logger.error(f"FFmpeg conversion error: {e.stderr}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to convert audio format: {e.stderr}"
                )
            
            # Verify the output file exists and has content
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create valid audio file"
                )
            
            # Use SpeechRecognition to convert audio to text
            with sr.AudioFile(output_path) as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                logger.info("Recording audio...")
                audio = self.recognizer.record(source)
                
                logger.info("Converting speech to text...")
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    logger.info(f"Successfully converted speech to text: {text[:100]}...")
                    return text
                except sr.UnknownValueError:
                    logger.error("Speech recognition could not understand audio")
                    raise HTTPException(
                        status_code=400,
                        detail="Could not understand audio. Please speak more clearly."
                    )
                except sr.RequestError as e:
                    logger.error(f"Speech recognition service error: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Could not request results from speech recognition service; {str(e)}"
                    )
                
        except Exception as e:
            logger.error(f"Unexpected error in speech-to-text conversion: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Clean up temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info("Cleaned up temporary directory")
                except Exception as e:
                    logger.error(f"Error cleaning up temporary directory: {str(e)}") 
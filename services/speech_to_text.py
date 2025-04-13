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
import platform
from typing import Optional

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self):
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Use system FFmpeg installation
            self.ffmpeg_path = "ffmpeg"
            
            logger.info(f"Initializing SpeechToTextService with ffmpeg path: {self.ffmpeg_path}")
            self._check_ffmpeg()
        except Exception as e:
            logger.error(f"Failed to initialize SpeechToTextService: {str(e)}")
            raise HTTPException(status_code=500, detail="Speech-to-text service initialization failed")

    def _check_ffmpeg(self) -> None:
        """Check if ffmpeg is available in the system."""
        try:
            result = subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError("FFmpeg is not properly installed or accessible")
            logger.info("FFmpeg is available: %s", result.stdout.split('\n')[0])
        except Exception as e:
            logger.error("FFmpeg check failed: %s", str(e))
            raise RuntimeError("FFmpeg is not properly installed or accessible") from e

    def _convert_webm_to_wav(self, webm_path: str) -> str:
        """Convert WebM audio to WAV format using ffmpeg."""
        try:
            wav_path = tempfile.mktemp(suffix=".wav")
            cmd = [
                self.ffmpeg_path,
                "-i", webm_path,
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                wav_path
            ]
            logger.info("Converting WebM to WAV: %s", " ".join(cmd))
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("FFmpeg conversion failed: %s", result.stderr)
                raise RuntimeError(f"Failed to convert audio: {result.stderr}")
            return wav_path
        except Exception as e:
            logger.error("Audio conversion failed: %s", str(e))
            raise

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
                    detail="Failed to convert audio format"
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
                        detail="Could not request results from speech recognition service"
                    )
                
        except Exception as e:
            logger.error(f"Unexpected error in speech-to-text conversion: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to convert speech to text")
        finally:
            # Clean up temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info("Cleaned up temporary directory")
                except Exception as e:
                    logger.error(f"Error cleaning up temporary directory: {str(e)}")
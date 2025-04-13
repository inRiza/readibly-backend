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

    def convert_audio_to_text(self, audio_path: str) -> str:
        """Convert audio file to text using Google Speech Recognition."""
        try:
            logger.info("Starting audio to text conversion for file: %s", audio_path)
            
            # Convert WebM to WAV if needed
            if audio_path.endswith('.webm'):
                wav_path = self._convert_webm_to_wav(audio_path)
                try:
                    with sr.AudioFile(wav_path) as source:
                        logger.info("Reading audio file: %s", wav_path)
                        audio = self.recognizer.record(source)
                        logger.info("Audio recorded, starting recognition")
                        text = self.recognizer.recognize_google(audio)
                        logger.info("Recognition successful")
                        return text
                finally:
                    if os.path.exists(wav_path):
                        os.remove(wav_path)
                        logger.info("Cleaned up temporary WAV file")
            else:
                with sr.AudioFile(audio_path) as source:
                    logger.info("Reading audio file: %s", audio_path)
                    audio = self.recognizer.record(source)
                    logger.info("Audio recorded, starting recognition")
                    text = self.recognizer.recognize_google(audio)
                    logger.info("Recognition successful")
                    return text
        except sr.UnknownValueError:
            logger.error("Speech recognition could not understand audio")
            raise RuntimeError("Could not understand the audio")
        except sr.RequestError as e:
            logger.error("Speech recognition service error: %s", str(e))
            raise RuntimeError(f"Speech recognition service error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during speech recognition: %s", str(e))
            raise RuntimeError(f"Failed to convert audio to text: {str(e)}")
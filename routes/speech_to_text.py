from fastapi import APIRouter, UploadFile, File, HTTPException
from services.speech_to_text import SpeechToTextService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
speech_service = SpeechToTextService()

@router.post("/speech-to-text")
async def convert_speech_to_text(audio: UploadFile = File(...)):
    """
    Convert uploaded audio file to text using speech recognition.
    """
    logger.info(f"Received audio file: {audio.filename}")
    
    if not audio.filename.endswith('.webm'):
        logger.warning(f"Invalid file type received: {audio.filename}")
        raise HTTPException(status_code=400, detail="Only WebM files are supported")
    
    try:
        logger.info("Starting speech-to-text conversion")
        text = await speech_service.convert_audio_to_text(audio)
        logger.info("Successfully converted speech to text")
        return {"text": text}
    except Exception as e:
        logger.error(f"Error in speech-to-text conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
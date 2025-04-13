from fastapi import APIRouter, UploadFile, File, HTTPException
from services.speech_to_text import SpeechToTextService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the service only when needed
def get_speech_service():
    try:
        return SpeechToTextService()
    except Exception as e:
        logger.error(f"Failed to initialize speech service: {str(e)}")
        raise HTTPException(status_code=500, detail="Speech-to-text service is not available")

@router.post("/speech-to-text")
async def convert_speech_to_text(audio: UploadFile = File(...)):
    """
    Convert uploaded audio file to text using speech recognition.
    """
    try:
        logger.info(f"Received audio file: {audio.filename}")
        
        if not audio.filename.endswith('.webm'):
            logger.warning(f"Invalid file type received: {audio.filename}")
            raise HTTPException(status_code=400, detail="Only WebM files are supported")
        
        # Initialize service only when needed
        speech_service = get_speech_service()
        
        logger.info("Starting speech-to-text conversion")
        text = await speech_service.convert_audio_to_text(audio)
        logger.info("Successfully converted speech to text")
        return {"text": text}
    except HTTPException as e:
        # Re-raise HTTP exceptions as they are
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in speech-to-text conversion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process speech-to-text request") 
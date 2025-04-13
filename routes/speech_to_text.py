from fastapi import APIRouter, UploadFile, File, HTTPException
from services.speech_to_text import SpeechToTextService
import logging
import os
import tempfile

logger = logging.getLogger(__name__)
router = APIRouter()
speech_to_text_service = SpeechToTextService()

@router.post("/api/speech-to-text")
async def convert_speech_to_text(audio: UploadFile = File(...)):
    try:
        logger.info("Received speech-to-text request")
        
        # Validate file type
        if not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        try:
            # Save the uploaded file
            content = await audio.read()
            temp_file.write(content)
            temp_file.close()
            
            # Convert audio to text
            text = speech_to_text_service.convert_audio_to_text(temp_file.name)
            logger.info("Successfully converted audio to text")
            return {"text": text}
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                logger.info("Cleaned up temporary audio file")
    except Exception as e:
        logger.error(f"Error in speech-to-text conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
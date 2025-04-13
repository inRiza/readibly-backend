from fastapi import APIRouter, UploadFile, File, HTTPException
from services.speech_to_text import SpeechToTextService
import logging

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
        
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{audio.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        try:
            # Convert audio to text
            text = speech_to_text_service.convert_audio_to_text(temp_file_path)
            logger.info("Successfully converted audio to text")
            return {"text": text}
        finally:
            # Clean up the temporary file
            import os
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info("Cleaned up temporary audio file")
    except Exception as e:
        logger.error(f"Error in speech-to-text conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
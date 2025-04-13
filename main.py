from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import json
import logging
import shutil
import uuid
import PyPDF2
import io
from dotenv import load_dotenv
from routes.auth.router import router as auth_router
from database import Base, engine
from models.user import User

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize database
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

# Initialize FastAPI app
app = FastAPI(
    title="Readibly API",
    description="API for Readibly application",
    version="1.0.0"
)

# Get allowed origins from environment variable or use default
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://readibly.vercel.app").split(",")
logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

# Configure CORS with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# Add OPTIONS handler for all routes
@app.options("/{path:path}")
async def options_handler(path: str):
    return {
        "status": "ok",
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600"
        }
    }

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received {request.method} request to {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    logger.info(f"Received file upload request: {file.filename}")
    
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            logger.warning(f"Invalid file type received: {file.filename}")
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Read file content
        content = await file.read()
        logger.info(f"Successfully read file, size: {len(content)} bytes")
        
        # Process PDF
        pdf_file = io.BytesIO(content)
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            logger.info(f"Successfully created PDF reader object with {len(pdf_reader.pages)} pages")
        except Exception as e:
            logger.error(f"Failed to create PDF reader: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid PDF file")
        
        text_content = ""
        
        # Extract text from all pages
        for page_num in range(len(pdf_reader.pages)):
            try:
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
                logger.info(f"Successfully extracted text from page {page_num + 1}")
            except Exception as e:
                logger.error(f"Error extracting text from page {page_num + 1}: {str(e)}")
                continue
        
        # Prepare response
        response_data = {
            "status": "success",
            "text": text_content,
            "words": text_content.split(),
            "pageCount": len(pdf_reader.pages)
        }
        
        logger.info("Successfully processed PDF")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/pdf/{filename}")
async def get_pdf(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/pdf")

@app.get("/")
async def root():
    return {"message": "Welcome to Readibly API"}

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Application startup complete")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
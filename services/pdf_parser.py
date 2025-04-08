import PyPDF2
import logging
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        self.supported_extensions = ['.pdf']

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Replace multiple newlines with single newline
        text = re.sub(r'\n\s*\n', '\n', text)
        # Ensure proper spacing around punctuation
        text = re.sub(r'([.,!?])', r' \1 ', text)
        return text.strip()

    def parse_pdf(self, file_path: str) -> dict:
        """
        Parse a PDF file and extract text content page by page.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            dict: Dictionary containing page numbers as keys and text content as values,
                 plus total number of pages
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")

            if not any(file_path.lower().endswith(ext) for ext in self.supported_extensions):
                logger.error(f"Unsupported file format: {file_path}")
                raise ValueError(f"Unsupported file format. Supported formats: {', '.join(self.supported_extensions)}")

            logger.info(f"Opening PDF file: {file_path}")
            with open(file_path, 'rb') as file:
                # Create PDF reader object
                reader = PyPDF2.PdfReader(file)
                
                # Get number of pages
                num_pages = len(reader.pages)
                logger.info(f"PDF has {num_pages} pages")
                
                # Extract text from each page
                content = {}
                for i in range(num_pages):
                    page = reader.pages[i]
                    content[i + 1] = page.extract_text()
                    logger.info(f"Extracted text from page {i + 1}")
                
                return {
                    "content": content,
                    "total_pages": num_pages
                }
                
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}") 
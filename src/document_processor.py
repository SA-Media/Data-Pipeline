from PyPDF2 import PdfReader
from docx import Document
import os
import warnings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.supported_extensions = {'.pdf', '.docx'}
        # Suppress PyPDF2 warnings about float objects
        warnings.filterwarnings('ignore', category=UserWarning, module='PyPDF2')

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX files."""
        extension = os.path.splitext(file_path)[1].lower()
        
        if extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {extension}")
        
        try:
            if extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif extension == '.docx':
                return self._extract_from_docx(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""  # Return empty string on error instead of failing

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = []
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    try:
                        extracted_text = page.extract_text()
                        if extracted_text:
                            text.append(extracted_text)
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num} in {file_path}: {str(e)}")
                        continue
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {str(e)}")
            return ""
            
        return "\n".join(text) if text else ""

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            full_text = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(full_text)
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path}: {str(e)}")
            return "" 
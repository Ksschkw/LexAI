# Purpose: Extracts text from the Nigerian Constitution PDF and chunks it for vector storage.
# Why: Preprocessing is critical for RAG—explicitly separating this logic keeps the model clean.

from pypdf import PdfReader
import re
import sys
import os
from utils.logger import logger
import time

# Dynamically adjust path to include project root when run directly
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.settings import settings

class DocumentManager:
    """Manages document extraction and chunking for LEXAI."""
    
    def __init__(self, chunk_size=settings.CHUNK_SIZE, overlap=settings.OVERLAP):
        """Initializes with chunk size and overlap from settings."""
        self.chunk_size = chunk_size  # Size of each text chunk in words
        self.overlap = overlap        # Overlap between chunks in words
        if self.overlap >= self.chunk_size:
            raise ValueError("Overlap must be less than chunk_size")
        logger.info(f"Initialized DocumentManager with chunk_size={self.chunk_size}, overlap={self.overlap}")
    
    def extract_from_pdf(self, pdf_path=settings.CONSTITUTION_PATH):
        """Extracts and cleans text from the Nigerian Constitution PDF.
        
        Args:
            pdf_path (str): Path to the PDF file.
        Returns:
            str: Cleaned text from the PDF.
        Raises:
            FileNotFoundError: If the PDF file is missing.
            ValueError: If no text is extracted.
        """
        logger.info(f"Attempting to extract text from {pdf_path}")
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                    logger.debug(f"Extracted text from page {page_num}")
                else:
                    logger.warning(f"No text extracted from page {page_num}")
            if not text:
                raise ValueError("No text extracted from the PDF.")
            # Clean up extra newlines and spaces
            cleaned_text = re.sub(r'\n\s*\n', '\n', text).strip()
            logger.info(f"Extracted and cleaned {len(cleaned_text)} characters of text")
            return cleaned_text
        except FileNotFoundError:
            logger.error(f"PDF not found at {pdf_path}")
            raise
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def chunk_document(self, content):
        """Splits text into chunks with overlap for vector storage.
        
        Args:
            content (str): Raw text to chunk.
        Returns:
            list: List of text chunks.
        """
        logger.info(f"Chunking document with {len(content.split())} words")
        words = content.split()
        total_words = len(words)
        chunks = []
        start = 0
        effective_step = self.chunk_size - self.overlap  # Net advancement per chunk
        
        start_time = time.time()
        while start < total_words:
            end = min(start + self.chunk_size, total_words)
            if end - start < self.chunk_size * 0.5:  # If less than half a chunk remains, stop
                chunk = ' '.join(words[start:end])
                if chunk.strip():
                    chunks.append(chunk)
                break
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start += effective_step
            if len(chunks) % 50 == 0:  # Log progress every 50 chunks
                elapsed = time.time() - start_time
                logger.info(f"Processed {len(chunks)} chunks in {elapsed:.2f} seconds")
            if time.time() - start_time > 300:  # 5-minute timeout
                logger.error("Chunking exceeded 5-minute timeout—aborting")
                break
        elapsed = time.time() - start_time
        expected_chunks = (total_words + self.chunk_size - 1) // effective_step  # Ceiling division
        logger.info(f"Created {len(chunks)} chunks in {elapsed:.2f} seconds (expected ~{expected_chunks})")
        return chunks
    
    def preprocess(self):
        """Runs the full preprocessing pipeline.
        
        Returns:
            list: List of document chunks ready for vector storage.
        """
        logger.info("Starting preprocessing pipeline")
        raw_text = self.extract_from_pdf(settings.CONSTITUTION_PATH)
        return self.chunk_document(raw_text)

if __name__ == "__main__":
    # Run preprocessing if script is executed directly
    logger.info("Executing document.py as main script")
    dm = DocumentManager()
    try:
        chunks = dm.preprocess()
        if not chunks:
            logger.warning("No chunks generated—check extraction or chunking logic")
        with open("constitution_chunks.json", "w", encoding="utf-8") as f:
            import json
            json.dump(chunks, f, ensure_ascii=False)
        logger.info(f"Successfully saved {len(chunks)} chunks to constitution_chunks.json")
        print(f"Extracted and saved {len(chunks)} chunks to constitution_chunks.json")
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        print(f"Error during preprocessing: {str(e)}")
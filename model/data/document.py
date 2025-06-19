# Purpose: Extracts text from the Nigerian Constitution PDF and chunks it for vector storage.
# Why: Preprocessing is critical for RAG—explicitly separating this logic keeps the model clean.

from pypdf import PdfReader
import re
import sys
import os
from utils.logger import logger
import time
import json

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
        """Extracts and cleans text from the Nigerian Constitution PDF."""
        logger.info(f"Attempting to extract text from {pdf_path}")
        try:
            reader = PdfReader(pdf_path)
            text = ""
            empty_pages = []
            
            for page_num, page in enumerate(reader.pages, 1):
                # Skip known empty pages
                if page_num in [1, 2, 6, 272, 273]:
                    empty_pages.append(page_num)
                    continue
                    
                page_text = page.extract_text()
                if page_text:
                    # Clean text
                    page_text = re.sub(r'\s+', ' ', page_text).strip()
                    text += f"\nPAGE {page_num}: {page_text}"
                else:
                    logger.warning(f"Page {page_num} has no extractable text")
                    empty_pages.append(page_num)
            
            if empty_pages:
                logger.info(f"Skipped {len(empty_pages)} empty pages: {empty_pages}")
            
            if not text.strip():
                raise ValueError("No text extracted from the PDF.")
                
            return text
        except FileNotFoundError:
            logger.error(f"PDF not found at {pdf_path}")
            raise
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def chunk_document(self, content):
        """Splits text into chunks with overlap for vector storage."""
        logger.info(f"Chunking document with {len(content.split())} words")
        words = content.split()
        total_words = len(words)
        chunks = []
        start = 0
        effective_step = self.chunk_size - self.overlap
        
        while start < total_words:
            end = min(start + self.chunk_size, total_words)
            if end - start < self.chunk_size * 0.5:
                chunk = ' '.join(words[start:end])
                if chunk.strip():
                    chunks.append(chunk)
                break
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start += effective_step
        return chunks
    
    def preprocess(self):
        """Runs the full preprocessing pipeline."""
        logger.info("Starting preprocessing pipeline")
        raw_text = self.extract_from_pdf()
        chunks = self.chunk_document(raw_text)
        
        # Add section tracking
        tagged_chunks = []
        current_chapter = "PREAMBLE"
        
        for chunk in chunks:
            # Detect chapter headers
            chapter_match = re.search(r'CHAPTER [IVX]+', chunk)
            if chapter_match:
                current_chapter = chapter_match.group(0)
            
            # Preserve metadata
            tagged_chunks.append({
                "content": chunk,
                "metadata": {
                    "chapter": current_chapter,
                    "is_fundamental_rights": 1 if "CHAPTER IV" in current_chapter else 0
                }
            })
        
        return tagged_chunks

if __name__ == "__main__":
    logger.info("Executing document preprocessing")
    dm = DocumentManager()
    try:
        chunks = dm.preprocess()
        with open("constitution_chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(chunks)} chunks to constitution_chunks.json")
        print(f"Extracted and saved {len(chunks)} chunks")
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        print(f"Error: {str(e)}")
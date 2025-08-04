# Purpose: Centralizes configuration settings and environment variables for LEXAI.
# Why: Explicitly defining settings avoids hardcoding and makes the app configurable.

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Encapsulates all configuration settings for LEXAI."""
    # API key for Groq, required for LLM access
    # API_KEY = os.getenv("GROQ_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise ValueError("API_KEY must be set in .env file for LLM access")
    
    # # Model name for Groq LLM, chosen for free tier compatibility
    # MODEL_NAME = "llama3-8b-8192"
    MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free"
    
    # Chunk size for document splitting (words), balances context and performance
    CHUNK_SIZE = 300
    
    # Overlap between chunks (words), ensures continuity in context
    OVERLAP = 50
    
    # Path to Nigerian Constitution PDF, update this before running
    CONSTITUTION_PATH = "Constitution-of-the-Federal-Republic-of-Nigeria.pdf"

# Instantiate settings for global access
settings = Settings()
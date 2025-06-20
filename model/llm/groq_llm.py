import requests
import json
from config.settings import settings
import logging

logger = logging.getLogger("LEXAI")

class GroqLLM:
    """Proper Groq API implementation matching official documentation."""
    
    def __init__(self):
        self.api_key = settings.API_KEY
        self.model_name = settings.MODEL_NAME
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def predict(self, messages):
        """Generates a response using Groq API with proper formatting."""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1,
            "stop": None,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload  # Use json parameter instead of data
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            if hasattr(response, 'text'):
                logger.error(f"Response content: {response.text}")
            raise RuntimeError(f"Failed to get response from Groq API")
    
    def get_llm(self):
        """Returns self for compatibility."""
        return self
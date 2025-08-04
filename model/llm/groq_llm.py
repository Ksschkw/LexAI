# import requests
# import json
# from config.settings import settings
# import logging

# logger = logging.getLogger("LEXAI")

# class GroqLLM:
#     """Proper Groq API implementation matching official documentation."""
    
#     def __init__(self):
#         self.api_key = settings.API_KEY
#         self.model_name = settings.MODEL_NAME
#         self.base_url = "https://api.groq.com/openai/v1/chat/completions"
#         self.headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json"
#         }
    
#     def predict(self, messages):
#         """Generates a response using Groq API with proper formatting."""
#         payload = {
#             "model": self.model_name,
#             "messages": messages,
#             "temperature": 0.7,
#             "max_tokens": 1024,
#             "top_p": 1,
#             "stop": None,
#             "stream": False
#         }
        
#         try:
#             response = requests.post(
#                 self.base_url,
#                 headers=self.headers,
#                 json=payload  # Use json parameter instead of data
#             )
#             response.raise_for_status()
#             return response.json()["choices"][0]["message"]["content"]
#         except Exception as e:
#             logger.error(f"Groq API error: {str(e)}")
#             if hasattr(response, 'text'):
#                 logger.error(f"Response content: {response.text}")
#             raise RuntimeError(f"Failed to get response from Groq API")
    
#     def get_llm(self):
#         """Returns self for compatibility."""
#         return self

import requests
import json
from config.settings import settings
import logging

logger = logging.getLogger("LEXAI")

class GroqLLM:
    """DeepSeek via OpenRouter API with fallback models for resilience."""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # List of fallback models, prioritize based on performance
        self.model_options = [
            settings.MODEL_NAME,
            "deepseek/deepseek-r1-0528:free",  # Primary model (e.g., deepseek/deepseek-v2)
            "deepseek/deepseek-chat",  # Fallback 1
            "deepseek/deepseek-r1:free"  # Fallback 2, if Groq API key is set up
        ]
    
    def predict(self, messages):
        """Generates a response using OpenRouter's DeepSeek API with fallbacks."""
        for model in self.model_options:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1,
                "stop": None,
                "stream": False
            }
            
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                logger.info(f"Successfully used model: {model}")
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"Model {model} failed: {str(e)}")
                if 'response' in locals():
                    logger.warning(f"Response content: {response.text}")
                continue  # Try the next model
        raise RuntimeError("All model fallbacks failed to respond")
    
    def get_llm(self):
        """Returns self for compatibility."""
        return self
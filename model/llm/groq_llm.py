# Purpose: Provides a clean interface to the Groq LLM.
# Why: Explicit wrapper avoids tight coupling with SwarmaURI’s implementation.

from swarmauri.standard.llms.concrete.GroqModel import GroqModel
from config.settings import settings

class GroqLLM:
    """Wrapper for GroqModel to handle LLM interactions."""
    
    def __init__(self):
        """Initializes the Groq LLM with API key and model name."""
        self.llm = GroqModel(api_key=settings.API_KEY, name=settings.MODEL_NAME)
    
    def generate(self, prompt):
        """Generates a response from the LLM.
        
        Args:
            prompt (str): The input prompt for the LLM.
        Returns:
            str: The LLM’s response.
        """
        return self.llm.predict(prompt)
    
    def get_llm(self):
        """Returns the underlying GroqModel instance.
        
        Returns:
            GroqModel: The LLM instance.
        """
        return self.llm
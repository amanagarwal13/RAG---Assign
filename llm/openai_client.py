import os
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIClient:
    """
    Integration with OpenAI API for LLM capabilities.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 3000
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to env var)
            model: Model to use (defaults to env var or a default model)
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini-2024-07-18")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, prompt: str) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        logger.info(f"Generating with OpenAI using model: {self.model}")
        
        try:
            # Make API request using OpenAI client
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the generated text
            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content.strip()
            
            logger.warning("No choices returned from OpenAI")
            return "I encountered an issue generating a response."
        
        except Exception as e:
            logger.error(f"Error generating with OpenAI: {str(e)}", exc_info=True)
            return f"Error: Could not generate text. {str(e)}"
    
    def generate_with_metadata(self, prompt: str) -> Dict[str, Any]:
        """
        Generate text and return with metadata.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Dictionary with generated text and metadata
        """
        logger.info(f"Generating with metadata using model: {self.model}")
        
        try:
            # Make API request using OpenAI client
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the generated text and metadata
            result = {
                "text": "I encountered an issue generating a response.",
                "model": self.model,
                "usage": {}
            }
            
            if completion.choices and len(completion.choices) > 0:
                result["text"] = completion.choices[0].message.content.strip()
            
            # Add usage information if available
            if hasattr(completion, 'usage'):
                result["usage"] = {
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                    "total_tokens": completion.usage.total_tokens
                }
            
            return result
        
        except Exception as e:
            logger.error(f"Error generating with OpenAI: {str(e)}", exc_info=True)
            return {
                "text": f"Error: Could not generate text. {str(e)}",
                "model": self.model,
                "error": str(e)
            } 
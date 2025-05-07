import os
import logging
import requests
import json
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DictionaryTool:
    """
    Tool for retrieving definitions of terms and concepts.
    """
    
    def __init__(self):
        """Initialize the dictionary tool."""
        # API URL for dictionary lookups (using Free Dictionary API)
        self.api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
        
        # Fallback to LLM if API fails
        # This will be initialized only when needed
        self.llm = None
    
    def execute(self, term: str) -> str:
        """
        Get the definition of a term.
        
        Args:
            term: The term to define
            
        Returns:
            String containing the definition(s)
        """
        logger.info(f"Dictionary processing term: {term}")
        
        # Clean up the term
        term = self._clean_term(term)
        logger.info(f"Cleaned term: {term}")
        
        # Try to get definition from the API
        try:
            definition = self._get_definition_from_api(term)
            if definition:
                return definition
        except Exception as e:
            logger.warning(f"API lookup failed: {str(e)}")
        
        # Fallback to LLM-based definition
        return self._get_definition_from_llm(term)
    
    def _clean_term(self, term: str) -> str:
        """
        Clean up the term for API lookup.
        
        Args:
            term: The term to clean
            
        Returns:
            Cleaned term
        """
        # Remove articles, quote marks, and trailing punctuation
        term = re.sub(r'^(a|an|the)\s+', '', term, flags=re.IGNORECASE)
        term = re.sub(r'["\']', '', term)
        term = re.sub(r'[.,;:!?]+$', '', term)
        
        # Extract the main term if there are qualifiers
        # For example: "apple in computing" -> "apple"
        main_term_match = re.match(r'^([\w\s-]+?)(?:\s+in\s+|\s+for\s+|\s+as\s+)', term, re.IGNORECASE)
        if main_term_match:
            term = main_term_match.group(1).strip()
        
        return term.strip().lower()
    
    def _get_definition_from_api(self, term: str) -> Optional[str]:
        """
        Get definition from the Dictionary API.
        
        Args:
            term: The term to look up
            
        Returns:
            Formatted definition string or None if not found
        """
        # Replace spaces with %20 for URL
        encoded_term = term.replace(' ', '%20')
        url = self.api_url.format(encoded_term)
        
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Format the response
            return self._format_api_response(data, term)
        else:
            logger.warning(f"API returned status code {response.status_code}")
            return None
    
    def _format_api_response(self, data: List[Dict[str, Any]], term: str) -> str:
        """
        Format the API response into a readable definition.
        
        Args:
            data: API response data
            term: The original term
            
        Returns:
            Formatted definition string
        """
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        # Get the first entry (most relevant)
        entry = data[0]
        
        # Initialize the result
        result = f"Definition of '{term}':\n\n"
        
        # Add phonetics if available
        if 'phonetic' in entry and entry['phonetic']:
            result += f"Pronunciation: {entry['phonetic']}\n\n"
        
        # Process each meaning
        if 'meanings' in entry and entry['meanings']:
            for i, meaning in enumerate(entry['meanings']):
                part_of_speech = meaning.get('partOfSpeech', 'unknown')
                result += f"{i+1}. {part_of_speech.capitalize()}\n"
                
                if 'definitions' in meaning and meaning['definitions']:
                    # Add definitions
                    for j, definition in enumerate(meaning['definitions']):
                        result += f"   {chr(97+j)}) {definition.get('definition', '')}\n"
                        
                        # Add example if available
                        if 'example' in definition and definition['example']:
                            result += f"      Example: \"{definition['example']}\"\n"
                
                # Add synonyms if available
                if 'synonyms' in meaning and meaning['synonyms']:
                    synonyms = ', '.join(meaning['synonyms'][:5])  # Limit to 5 synonyms
                    result += f"   Synonyms: {synonyms}\n"
                
                result += "\n"
        
        return result.strip()
    
    def _get_definition_from_llm(self, term: str) -> str:
        """
        Get definition using the LLM as a fallback.
        
        Args:
            term: The term to define
            
        Returns:
            Definition string from the LLM
        """
        # Import here to avoid circular import
        from llm.openai_client import OpenAIClient
        
        if self.llm is None:
            self.llm = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create a prompt for the LLM
        prompt = f"""
        Please provide a clear and concise definition of the term "{term}".
        Include:
        1. The part of speech (noun, verb, adjective, etc.)
        2. The primary definition
        3. Any secondary meanings if relevant
        4. A brief example of usage if helpful
        
        Format your response as a dictionary entry.
        """
        
        # Get definition from LLM
        response = self.llm.generate(prompt)
        
        # Format the response if needed
        if not response.startswith(f"Definition of '{term}'"):
            response = f"Definition of '{term}':\n\n{response}"
        
        return response
import os
import logging
import re
from typing import Dict, Any, List

from .calculator import CalculatorTool
from .dictionary import DictionaryTool
from rag.retriever import DocumentRetriever
from llm.openai_client import OpenAIClient

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates the agent workflow, routing queries to appropriate tools
    and managing the overall processing pipeline.
    """
    
    def __init__(self, vector_store):
        """
        Initialize the orchestrator with necessary components.
        
        Args:
            vector_store: Vector store instance for document retrieval
        """
        self.vector_store = vector_store
        self.llm = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize tools
        self.calculator_tool = CalculatorTool()
        self.dictionary_tool = DictionaryTool()
        self.retriever = DocumentRetriever(vector_store, self.llm)
        
        # Decision keywords
        self.calculator_keywords = [
            "calculate", "computation", "solve", "equation", "arithmetic", 
            "add", "subtract", "multiply", "divide", "sum"
        ]
        
        self.dictionary_keywords = [
            "define", "define the", "define a", "define an"
        ]
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query by determining the appropriate tool and executing it.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Log the incoming query
        logger.info(f"Processing query: {query}")
        
        # Determine which tool to use
        tool_decision = self._determine_tool(query)
        tool_name = tool_decision["tool"]
        decision_reason = tool_decision["reason"]
        
        logger.info(f"Selected tool: {tool_name} - Reason: {decision_reason}")
        
        # Initialize the response structure
        response = {
            "query": query,
            "tool_used": tool_name,
            "decision_reason": decision_reason,
            "context_snippets": [],
            "answer": "",
            "success": True
        }
        
        try:
            # Route to the appropriate tool
            if tool_name == "calculator":
                result = self.calculator_tool.execute(query)
                response["answer"] = result
                
            elif tool_name == "dictionary":
                term = self._extract_term_to_define(query)
                result = self.dictionary_tool.execute(term)
                response["answer"] = result
                
            else:  # RAG pipeline
                retrieval_result = self.retriever.retrieve_and_generate(query)
                response["context_snippets"] = retrieval_result["context_snippets"]
                response["answer"] = retrieval_result["answer"]
        
        except Exception as e:
            logger.error(f"Error processing with {tool_name}: {str(e)}", exc_info=True)
            response["success"] = False
            response["error"] = str(e)
            # Fallback to RAG if another tool fails
            if tool_name != "rag":
                logger.info("Falling back to RAG pipeline")
                try:
                    retrieval_result = self.retriever.retrieve_and_generate(query)
                    response["context_snippets"] = retrieval_result["context_snippets"]
                    response["answer"] = retrieval_result["answer"]
                    response["tool_used"] = "rag (fallback)"
                    response["success"] = True
                except Exception as fallback_e:
                    response["error"] += f" | Fallback error: {str(fallback_e)}"
        
        return response
    
    def _determine_tool(self, query: str) -> Dict[str, str]:
        """
        Determine which tool to use based on the query.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with the selected tool name and reason
        """
        # Normalize query for keyword matching
        normalized_query = query.lower()
        
        # Check for calculator keywords
        for keyword in self.calculator_keywords:
            if keyword in normalized_query:
                # Additional check to confirm it's likely a calculation request
                if re.search(r'[\d+\-*/^().,]', query):
                    return {
                        "tool": "calculator",
                        "reason": f"Query contains calculation keyword '{keyword}' and numeric/operator characters"
                    }
        
        # Check for dictionary keywords
        for keyword in self.dictionary_keywords:
            if keyword in normalized_query:
                return {
                    "tool": "dictionary",
                    "reason": f"Query contains definition keyword '{keyword}'"
                }
        
        # Default to RAG
        return {
            "tool": "rag",
            "reason": "Query requires document knowledge"
        }
    
    def _extract_term_to_define(self, query: str) -> str:
        """
        Extract the term to be defined from a dictionary query.
        
        Args:
            query: The original query string
            
        Returns:
            The extracted term to define
        """
        # Try to extract using regex patterns
        patterns = [
            r'define\s+(?:the\s+(?:term|word|phrase)\s+)?["\']?([^"\'?]+)["\']?',
            r'what\s+(?:does|is|are)\s+(?:a|an|the)?\s+["\']?([^"\'?]+)["\']?',
            r'definition\s+of\s+["\']?([^"\'?]+)["\']?',
            r'meaning\s+of\s+["\']?([^"\'?]+)["\']?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no match with patterns, try a simpler approach
        for keyword in ["define", "what is", "what are", "definition of", "meaning of"]:
            if keyword in query.lower():
                # Extract everything after the keyword
                term = query.lower().split(keyword, 1)[1].strip()
                # Remove trailing punctuation
                term = re.sub(r'[.?!]$', '', term).strip()
                return term
        
        # If all else fails, return the query without common question words/punctuation
        cleaned_query = re.sub(r'^(what|who|where|when|why|how)\s+is\s+', '', query, flags=re.IGNORECASE)
        cleaned_query = re.sub(r'[.?!]$', '', cleaned_query).strip()
        return cleaned_query
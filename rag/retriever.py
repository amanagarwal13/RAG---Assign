import logging
from typing import Dict, List, Any
import re

logger = logging.getLogger(__name__)

# Constants for answer generation
MAX_CONTEXT_SNIPPETS = 3
MIN_RELEVANCE_SCORE = 0.5

class DocumentRetriever:
    """
    Retrieves relevant document chunks and generates answers using LLM.
    """
    
    def __init__(self, vector_store, llm, top_k: int = MAX_CONTEXT_SNIPPETS):
        """
        Initialize the document retriever.
        
        Args:
            vector_store: Vector store instance
            llm: LLM instance
            top_k: Number of documents to retrieve (default: MAX_CONTEXT_SNIPPETS)
        """
        self.vector_store = vector_store
        self.llm = llm
        self.top_k = top_k
    
    def retrieve_and_generate(self, query: str) -> Dict[str, Any]:
        """
        Retrieve relevant documents and generate an answer.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with answer and context snippets
        """
        logger.info(f"Retrieving documents for query: {query}")
        
        # Preprocess query
        processed_query = self._preprocess_query(query)
        
        # Search for relevant documents
        search_results = self.vector_store.search(processed_query, top_k=self.top_k)
        
        # Prepare context snippets
        context_snippets = []
        seen_sources = set()  # Track unique sources
        
        for result in search_results:
            # Skip if we've already seen this source (avoid duplicate information)
            source = result["metadata"].get("source", "Unknown")
            if source in seen_sources:
                continue
                
            # Skip low relevance results
            if result["score"] < MIN_RELEVANCE_SCORE:
                continue
                
            seen_sources.add(source)
            
            snippet = {
                "text": result["text"],
                "source": source,
                "relevance_score": f"{result['score']:.2f}",
                "metadata": result["metadata"]
            }
            context_snippets.append(snippet)
        
        # If no results found
        if not context_snippets:
            logger.warning(f"No documents found for query: {query}")
            return {
                "answer": "I don't have enough information to answer that question based on the available documents.",
                "context_snippets": []
            }
        
        # Generate answer using LLM with retrieved context
        answer = self._generate_answer(query, context_snippets)
        
        return {
            "answer": answer,
            "context_snippets": context_snippets
        }
    
    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess the query for better retrieval.
        
        Args:
            query: Original query
            
        Returns:
            Preprocessed query
        """
        # Remove punctuation except question marks
        query = re.sub(r'[^\w\s?]', ' ', query)
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    def _generate_answer(self, query: str, context_snippets: List[Dict[str, Any]]) -> str:
        """
        Generate an answer using the LLM based on the retrieved context.
        
        Args:
            query: User query
            context_snippets: Retrieved context snippets
            
        Returns:
            Generated answer string
        """
        # Sort snippets by relevance score
        sorted_snippets = sorted(context_snippets, 
                               key=lambda x: float(x['relevance_score']), 
                               reverse=True)
        
        # Prepare context string with source information
        context_parts = []
        for snippet in sorted_snippets:
            context_parts.append(
                f"Source: {snippet['source']}\n"
                f"Relevance: {snippet['relevance_score']}\n"
                f"Content: {snippet['text']}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        # Create prompt for the LLM
        prompt = f"""You are a helpful AI assistant that answers questions based on provided context.
        Your task is to provide accurate, well-structured answers using only the information given in the context.
        
        Guidelines:
        1. Use only the information provided in the context
        2. If the context doesn't contain the answer, say "I don't have enough information to answer that question"
        3. If there are conflicting pieces of information, acknowledge the conflict and explain the different perspectives
        4. Format your response in a clear, natural way
        5. Include relevant quotes from the context when appropriate
        6. Maintain a professional and helpful tone
        
        CONTEXT:
        {context}
        
        QUESTION:
        {query}
        
        Note: This response was generated by an AI system created by Aman Agarwal (amannagarwal13@gmail.com).
        
        ANSWER:
        """
        
        # Generate answer
        logger.info("Generating answer with LLM")
        return self.llm.generate(prompt)
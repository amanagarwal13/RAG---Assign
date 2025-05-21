import os
import logging
import time
from typing import List, Dict, Any, Optional
import pinecone
import numpy as np

from .document_processor import DocumentChunk
from .embeddings import OpenAILangChainEmbeddings

logger = logging.getLogger(__name__)

from pinecone import Pinecone, ServerlessSpec

# Constants for Pinecone configuration
DEFAULT_INDEX_NAME = "rag-agent-index"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"
DEFAULT_DIMENSIONS = {
    "text-embedding-3-large": 3072,
    "text-embedding-3-small": 1536,
    "text-embedding-ada-002": 1536
}
DEFAULT_METRIC = "cosine"
DEFAULT_CLOUD = "aws"
DEFAULT_REGION = "us-east-1"
INITIALIZATION_WAIT_TIME = 10  # seconds

class PineconeVectorStore:
    """
    Vector store implementation using Pinecone.
    """
    
    def __init__(
        self, 
        api_key: str = None, 
        index_name: str = None, 
        openai_api_key: str = None,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL
    ):
        """
        Initialize the Pinecone vector store.
        
        Args:
            api_key: Pinecone API key (defaults to env var)
            index_name: Name of the Pinecone index (defaults to env var)
            openai_api_key: OpenAI API key (defaults to env var)
            embedding_model: Name of the embedding model to use
        """
        # Get config from env vars if not provided
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", DEFAULT_INDEX_NAME)
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Pinecone API key is required")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for embeddings")
        
        # Initialize embedding generator using OpenAI via LangChain
        self.embedding_generator = OpenAILangChainEmbeddings(
            api_key=self.openai_api_key,
            model_name=embedding_model
        )
        
        # Set dimension based on model
        self.dimension = DEFAULT_DIMENSIONS.get(embedding_model)
        if not self.dimension:
            raise ValueError(f"Unsupported embedding model: {embedding_model}")
            
        logger.info(f"Using embedding model {embedding_model} with dimension {self.dimension}")
        
        # Initialize Pinecone
        self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and ensure index exists."""
        logger.info("Initializing Pinecone")

        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.api_key)

            # Check if index exists, create if not
            existing_indexes = self.pc.list_indexes().names()

            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=DEFAULT_METRIC,
                    spec=ServerlessSpec(
                        cloud=DEFAULT_CLOUD,
                        region=DEFAULT_REGION
                    )
                )
                # Wait for index to be ready
                logger.info(f"Waiting {INITIALIZATION_WAIT_TIME} seconds for index to be ready...")
                time.sleep(INITIALIZATION_WAIT_TIME)

            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")

        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}", exc_info=True)
            raise
    
    def add_documents(self, chunks: List[DocumentChunk]):
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of document chunks to add
        """
        if not chunks:
            logger.warning("No chunks to add to vector store")
            return
        
        logger.info(f"Adding {len(chunks)} chunks to Pinecone")
        
        try:
            # Convert chunks to texts for embedding
            texts = [chunk.text for chunk in chunks]
            
            # Generate embeddings using OpenAI via LangChain
            embeddings = self.embedding_generator.generate(texts)
            
            # Prepare vectors for upsert
            vectors = []
            for i, chunk in enumerate(chunks):
                vector = {
                    "id": chunk.id,
                    "values": embeddings[i].tolist(),
                    "metadata": chunk.metadata
                }
                vector["metadata"]["text"] = chunk.text
                vectors.append(vector)
            
            # Upsert vectors to Pinecone
            self.index.upsert(vectors=vectors)
            logger.info(f"Successfully added {len(vectors)} vectors to Pinecone")
        
        except Exception as e:
            logger.error(f"Error adding documents to Pinecone: {str(e)}", exc_info=True)
            raise
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for similar documents in the vector store.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of search results with text, metadata, and scores
        """
        logger.info(f"Searching Pinecone for: {query}")
        
        try:
            # Generate embedding for the query using OpenAI
            query_embedding = self.embedding_generator.generate(query)
            
            # Ensure we have a proper vector
            if not isinstance(query_embedding, np.ndarray):
                query_embedding = np.array(query_embedding)
            
            # Ensure we have the right shape (1, dimension)
            if len(query_embedding.shape) == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding[0].tolist(),  # Get first row and convert to list
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.get("matches", []):
                result = {
                    "id": match["id"],
                    "score": match["score"],
                    "text": match["metadata"].get("text", ""),
                    "metadata": {k: v for k, v in match["metadata"].items() if k != "text"}
                }
                formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching Pinecone: {str(e)}", exc_info=True)
            # Return empty results on error
            return []
    
    def delete_document(self, document_name: str):
        """
        Delete all chunks from a specific document.
        
        Args:
            document_name: Name of the document to delete
        """
        logger.info(f"Deleting document from Pinecone: {document_name}")
        
        try:
            # Query to find all chunks from this document
            query = {"source": document_name}
            
            # Find matching IDs
            result = self.index.query(
                vector=[0] * self.dimension,  # Dummy vector for metadata-only query
                top_k=10000,  # Large number to get all matches
                include_metadata=True,
                filter=query
            )
            
            # Extract IDs
            ids = [match["id"] for match in result.get("matches", [])]
            
            if ids:
                # Delete the vectors
                self.index.delete(ids=ids)
                logger.info(f"Deleted {len(ids)} chunks for document: {document_name}")
            else:
                logger.info(f"No chunks found for document: {document_name}")
                
        except Exception as e:
            logger.error(f"Error deleting document from Pinecone: {str(e)}", exc_info=True)
            raise
    
    def clear_index(self):
        """Delete all vectors in the index."""
        logger.warning(f"Clearing all vectors from index: {self.index_name}")
        
        try:
            self.index.delete(delete_all=True)
            logger.info("Index cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}", exc_info=True)
            raise

    def get_random_chunks(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get random chunks from the vector store.
        
        Args:
            limit: Number of random chunks to retrieve
            
        Returns:
            List of document chunks with text and metadata
        """
        logger.info(f"Getting {limit} random chunks from Pinecone")
        
        try:
            # Query with a random vector to get random results
            random_vector = np.random.randn(self.dimension).tolist()
            
            # Query Pinecone
            results = self.index.query(
                vector=random_vector,
                top_k=limit,
                include_metadata=True
            )
            
            # Format results
            chunks = []
            for match in results.get("matches", []):
                chunk = {
                    "text": match["metadata"].get("text", ""),
                    "metadata": {k: v for k, v in match["metadata"].items() if k != "text"}
                }
                chunks.append(chunk)
            
            logger.info(f"Retrieved {len(chunks)} random chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error getting random chunks: {str(e)}", exc_info=True)
            return []
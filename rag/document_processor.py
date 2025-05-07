import re
import logging
import uuid
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DocumentChunk:
    """
    Represents a chunk of a document with metadata.
    """
    
    def __init__(self, text: str, metadata: Dict[str, Any]):
        """
        Initialize a document chunk.
        
        Args:
            text: The text content of the chunk
            metadata: Metadata about the chunk (source, position, etc.)
        """
        self.id = str(uuid.uuid4())
        self.text = text
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the chunk to a dictionary.
        
        Returns:
            Dictionary representation of the chunk
        """
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata
        }

class DocumentProcessor:
    """
    Processes documents by chunking them into smaller pieces suitable for embedding.
    """
    
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between consecutive chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process(self, document_text: str, document_name: str) -> List[DocumentChunk]:
        """
        Process a document into chunks.
        
        Args:
            document_text: The full text of the document
            document_name: Name/identifier of the document
            
        Returns:
            List of document chunks
        """
        logger.info(f"Processing document: {document_name}")
        
        # Detect document type and preprocess if needed
        preprocessed_text = self._preprocess_document(document_text, document_name)
        
        # Split the document into chunks
        chunks = self._split_text(preprocessed_text, document_name)
        
        logger.info(f"Created {len(chunks)} chunks from document {document_name}")
        return chunks
    
    def _preprocess_document(self, text: str, document_name: str) -> str:
        """
        Preprocess the document based on its type/extension.
        
        Args:
            text: The document text
            document_name: Name of the document
            
        Returns:
            Preprocessed text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters and normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"['']", "'", text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)
        
        # Remove extra punctuation
        text = re.sub(r'([.,!?])\1+', r'\1', text)
        
        return text
    
    def _split_text(self, text: str, document_name: str) -> List[DocumentChunk]:
        """
        Split text into chunks using sentence boundaries.
        
        Args:
            text: The preprocessed document text
            document_name: Name of the document
            
        Returns:
            List of document chunks
        """
        chunks = []
        
        # Split into sentences using regex
        # This pattern matches sentence endings followed by space or end of string
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_size = 0
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_size = len(sentence)
            
            # If adding this sentence would exceed the chunk size,
            # save the current chunk and start a new one
            if current_size + sentence_size > self.chunk_size and current_chunk:
                # Create a chunk from the accumulated sentences
                chunk_text = ' '.join(current_chunk)
                chunks.append(self._create_chunk(chunk_text, document_name, len(chunks)))
                
                # Start a new chunk with overlap
                overlap_size = 0
                overlap_sentences = []
                
                # Add sentences from the end of the previous chunk until we reach the desired overlap
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_size = overlap_size
            
            # Add the current sentence to the chunk
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(self._create_chunk(chunk_text, document_name, len(chunks)))
        
        return chunks
    
    def _create_chunk(self, text: str, document_name: str, chunk_index: int) -> DocumentChunk:
        """
        Create a document chunk with metadata.
        
        Args:
            text: The chunk text
            document_name: Name of the document
            chunk_index: Index of the chunk in the document
            
        Returns:
            DocumentChunk instance
        """
        # Count sentences using regex
        sentences = re.split(r'(?<=[.!?])\s+', text)
        num_sentences = len([s for s in sentences if s.strip()])
        
        metadata = {
            "source": document_name,
            "chunk_index": chunk_index,
            "chunk_size": len(text),
            "num_sentences": num_sentences,
            "avg_sentence_length": len(text) / max(1, num_sentences)
        }
        
        return DocumentChunk(text, metadata)
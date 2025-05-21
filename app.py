"""
RAG-Powered Document Q&A System

This module implements a Flask-based web application that provides a RAG (Retrieval-Augmented Generation)
system for document-based question answering. It integrates with Pinecone for vector storage and OpenAI
for embeddings and text generation.

The application provides endpoints for:
- Document upload and processing
- Query processing and answer generation
- System initialization
- Question suggestions
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import json
import time
import logging
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# Import project modules
from rag.document_processor import DocumentProcessor
from rag.vector_store import PineconeVectorStore
from rag.retriever import DocumentRetriever
from llm.openai_client import OpenAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize components
try:
    document_processor = DocumentProcessor()
    vector_store = PineconeVectorStore(
        api_key=os.getenv("PINECONE_API_KEY"),
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    )
    llm = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
    retriever = DocumentRetriever(vector_store, llm)
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}", exc_info=True)
    raise

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a user query and return the response"""
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Process query through RAG pipeline
        start_time = time.time()
        result = retriever.retrieve_and_generate(query)
        processing_time = time.time() - start_time
        
        # Add processing time to result
        result['processing_time'] = f"{processing_time:.2f}s"
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['POST'])
def upload_documents():
    """Upload and process documents for the RAG system"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        processed_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # Process and ingest the document
            document_text = file.read().decode('utf-8')
            chunks = document_processor.process(document_text, file.filename)
            vector_store.add_documents(chunks)
            
            processed_files.append(file.filename)
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(processed_files)} documents',
            'processed_files': processed_files
        })
        
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/initialize', methods=['POST'])
def initialize_system():
    """Initialize the system with sample documents"""
    try:
        # Process sample documents in the data directory
        sample_docs_path = os.path.join(os.path.dirname(__file__), 'data')
        processed_files = []
        
        for filename in os.listdir(sample_docs_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(sample_docs_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    document_text = f.read()
                
                chunks = document_processor.process(document_text, filename)
                vector_store.add_documents(chunks)
                processed_files.append(filename)
        
        return jsonify({
            'success': True,
            'message': f'Initialized system with {len(processed_files)} documents',
            'processed_files': processed_files
        })
        
    except Exception as e:
        logger.error(f"Error initializing system: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents')
def get_documents():
    """Get contents of all documents in the data folder."""
    try:
        contents = {}
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents[filename] = f.read()
        
        return jsonify({
            'status': 'success',
            'contents': contents
        })
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve documents'
        }), 500

@app.route('/api/suggestions')
def get_suggestions():
    """Generate question suggestions based on the content in the vector database"""
    try:
        logger.info("Starting to generate suggestions")
        
        # Get a few random chunks from the vector database
        chunks = vector_store.get_random_chunks(limit=3)
        logger.info(f"Retrieved {len(chunks)} chunks from vector store")
        
        if not chunks:
            logger.warning("No chunks found in vector store")
            return jsonify({
                'suggestions': []
            })
        
        # Log the chunks we got
        for i, chunk in enumerate(chunks):
            logger.info(f"Chunk {i+1}: {chunk['text'][:100]}...")
        
        # Create a prompt for the LLM to generate questions
        prompt = f"""Based on the following text snippets from documents, generate 3 relevant questions that could be asked about this content.
        For each question, also provide a brief context about what part of the text it relates to.
        Return ONLY the JSON array of objects with 'question' and 'context' fields, without any markdown formatting or code block markers.

        Text snippets:
        {chr(10).join([f"- {chunk['text']}" for chunk in chunks])}

        Return the questions in this exact format:
        [
            {{
                "question": "What is the main topic discussed in the first snippet?",
                "context": "Based on the introduction section"
            }},
            ...
        ]"""

        logger.info("Sending prompt to LLM")
        # Generate questions using the LLM
        response = llm.generate(prompt)
        logger.info(f"Received response from LLM: {response[:200]}...")
        
        try:
            # Clean the response by removing any markdown code block markers
            cleaned_response = response.strip()
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.split('\n', 1)[1]  # Remove first line
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response.rsplit('\n', 1)[0]  # Remove last line
            if cleaned_response.startswith('json'):
                cleaned_response = cleaned_response.split('\n', 1)[1]  # Remove json marker
            
            # Parse the JSON response
            suggestions = json.loads(cleaned_response)
            logger.info(f"Successfully parsed {len(suggestions)} suggestions")
            return jsonify({
                'suggestions': suggestions
            })
        except json.JSONDecodeError as e:
            # If the response isn't valid JSON, return an empty list
            logger.warning(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.warning(f"Raw response: {response}")
            return jsonify({
                'suggestions': []
            })
            
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to generate suggestions'
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
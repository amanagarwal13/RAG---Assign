import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import json
import time
import logging

# Load environment variables
load_dotenv()

# Import project modules
from agents.orchestrator import AgentOrchestrator
from rag.document_processor import DocumentProcessor
from rag.vector_store import PineconeVectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize components
document_processor = DocumentProcessor()
vector_store = PineconeVectorStore(
    api_key=os.getenv("PINECONE_API_KEY"),
    index_name=os.getenv("PINECONE_INDEX_NAME"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
)
agent_orchestrator = AgentOrchestrator(vector_store)

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
        
        # Process query through agent orchestrator
        start_time = time.time()
        result = agent_orchestrator.process_query(query)
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
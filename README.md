# RAG-Powered Document Q&A System

A knowledge assistant that retrieves information from documents and generates natural-language answers using Retrieval-Augmented Generation (RAG).

## Features

- **Document Ingestion**: Upload and process text documents for knowledge retrieval
- **Vector Search**: Pinecone-powered semantic search to find relevant information
- **Smart Question Generation**: Automatically generates relevant questions based on document content
- **Modern UI**: Clean, responsive interface with real-time feedback
- **Explainable Results**: View source context and processing time for each query

## Architecture

### Components

1. **Web UI (Flask)**: 
   - Provides the user interface for interacting with the system
   - Handles document uploads, query input, and result display

2. **RAG Pipeline**:
   - **Document Processor**: Chunks documents for indexing
   - **Vector Store**: Pinecone-based vector database for efficient retrieval
   - **Retriever**: Finds the most relevant document chunks for a query
   - **LLM Integration**: Uses OpenAI to generate answers from retrieved context

## Getting Started

### Prerequisites

- Python 3.9+
- Pinecone account (for vector storage)
- OpenAI API key (for LLM access)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rag-powered-agent.git
   cd rag-powered-agent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=rag-agent-index
   FLASK_ENV=development
   FLASK_DEBUG=true
   ```

### Running the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Upload some text documents to populate the knowledge base.

4. Start asking questions!

## Usage Examples

### Calculator Tool
- "Calculate 125 * 37 - 42"
- "What is the square root of 144 plus 25?"
- "Solve 15% of 240"

### Dictionary Tool
- "Define artificial intelligence"
- "What is the meaning of quantum computing?"
- "Define retrieval-augmented generation"

### RAG Pipeline
- "What is the KRAG framework?"
- "What are the system requirements for cloud deployment?"
- "How many employees does RAG Technologies have?"

## API Endpoints

- `GET /`: Main application interface
- `POST /api/query`: Process a user query and return the response
- `POST /api/documents`: Upload and process documents
- `POST /api/initialize`: Initialize the system with sample documents
- `GET /api/documents`: Get contents of all documents in the data folder
- `GET /api/suggestions`: Generate question suggestions based on document content

## Project Structure

```
rag-powered-agent/
│
├── app.py                  # Main Flask application
├── wsgi.py                # WSGI entry point
├── requirements.txt        # Project dependencies
│
├── static/                 # Static files for the web UI
│   ├── css/
│   └── js/
│
├── templates/              # Flask HTML templates
│   └── index.html          # Main application interface
│
├── rag/                    # RAG pipeline components
│   ├── document_processor.py  # Document chunking and processing
│   ├── vector_store.py     # Pinecone integration
│   └── retriever.py        # Document retrieval logic
│
├── llm/                    # LLM integration
│   └── openai_client.py    # OpenAI API client
│
└── data/                   # Sample documents for ingestion
```

## Key Features

1. **Efficient Document Processing**:
   - Smart document chunking
   - Context-preserving text splitting
   - Support for multiple document formats

2. **Advanced Vector Search**:
   - OpenAI's text-embedding-3-large for semantic understanding
   - Pinecone's serverless architecture for scalability
   - Optimized retrieval for quick responses

3. **Smart Question Generation**:
   - Automatic question suggestions based on document content
   - Context-aware question generation
   - Relevant to the uploaded documents

4. **Reliable LLM Integration**:
   - Direct OpenAI integration
   - Context-aware response generation
   - Quality-focused answer generation


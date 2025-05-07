# RAG-Powered Multi-Agent Q&A Assistant

A knowledge assistant that retrieves information from documents, generates natural-language answers, and orchestrates its workflow through a basic agentic system.

## Features

- **Document Ingestion**: Upload and process text documents for knowledge retrieval
- **Vector Search**: Pinecone-powered semantic search to find relevant information
- **Multi-Agent Workflow**: Intelligently routes queries to specialized tools:
  - **Calculator**: Handles mathematical expressions and calculations
  - **Dictionary**: Provides definitions for terms and concepts
  - **RAG Pipeline**: Retrieves relevant information from documents and generates answers
- **Modern UI**: Clean, responsive interface with real-time feedback
- **Explainable Results**: View which tool was used, decision reasoning, and source context

## Architecture

### Components

1. **Web UI (Flask)**: 
   - Provides the user interface for interacting with the system
   - Handles document uploads, query input, and result display

2. **Agent Orchestrator**:
   - Analyzes queries to determine the appropriate tool
   - Routes requests to Calculator, Dictionary, or RAG Pipeline
   - Logs decision steps for transparency

3. **Tools**:
   - **Calculator**: Parses and evaluates mathematical expressions
   - **Dictionary**: Retrieves definitions of terms using an API or LLM fallback
   - **RAG Pipeline**: Finds relevant documents and generates answers

4. **RAG Pipeline**:
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

## Project Structure

```
rag-powered-agent/
│
├── app.py                  # Main Flask application
├── .env                    # Environment variables (API keys, etc.)
├── requirements.txt        # Project dependencies
│
├── static/                 # Static files for the web UI
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── main.js         # Client-side functionality
│
├── templates/              # Flask HTML templates
│   ├── index.html          # Main application interface
│   └── base.html           # Base template with common elements
│
├── agents/                 # Agent components
│   ├── __init__.py
│   ├── orchestrator.py     # Main agent orchestrator
│   ├── calculator.py       # Calculator tool
│   └── dictionary.py       # Dictionary tool
│
├── rag/                    # RAG pipeline components
│   ├── __init__.py
│   ├── document_processor.py  # Document chunking and processing
│   ├── embeddings.py       # Embedding generation
│   ├── vector_store.py     # Pinecone integration
│   └── retriever.py        # Document retrieval logic
│
├── llm/                    # LLM integration
│   ├── __init__.py
│   └── openai_client.py    # OpenAI API client
│
└── data/                   # Sample documents for ingestion
    ├── doc1.txt
    ├── doc2.txt
    └── doc3.txt
```

## Key Design Choices

1. **Modular Architecture**:
   - Clean separation between agents, RAG pipeline, and tools
   - Independent components that can be tested and modified in isolation
   - Extensible design for adding new capabilities
   - Maintainable codebase with clear responsibilities

2. **Intelligent Query Routing**:
   - Pattern-based query analysis for accurate tool selection
   - Support for multi-intent queries
   - Fallback mechanisms for edge cases
   - Detailed logging for system behavior analysis

3. **Efficient Vector Search**:
   - OpenAI's text-embedding-3-large for semantic understanding
   - Cosine similarity for relevance scoring
   - Pinecone's serverless architecture for scalability
   - Optimized retrieval for quick responses

4. **Smart Document Processing**:
   - Context-preserving document chunking
   - Configurable overlap for maintaining context
   - Rich metadata for better understanding
   - Support for multiple document formats

5. **Reliable LLM Integration**:
   - Direct OpenAI integration for consistent results
   - Context-aware response generation
   - Efficient context management
   - Quality-focused answer generation

6. **Transparent System**:
   - Clear decision-making process
   - Source tracking for all answers
   - Relevance scoring for retrieved documents
   - Detailed operation logging

7. **Error Management**:
   - Graceful handling of service disruptions
   - Comprehensive error tracking
   - Automatic recovery from transient issues
   - Clear user feedback

8. **Performance Considerations**:
   - Optimized vector operations
   - Efficient resource utilization
   - Smart caching strategies
   - Scalable architecture

9. **Security Measures**:
   - Secure credential management
   - Input validation
   - Request rate control
   - Environment-based settings

10. **Development Support**:
    - Structured logging
    - Clear documentation
    - Consistent code style
    - Straightforward deployment

## Future Enhancements

1. Support for more document types (PDF, DOCX, HTML)
2. Improved chunking with section awareness
3. Multi-language support
4. User feedback mechanism for answer quality
5. Knowledge graph integration
6. More specialized tools and agents

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
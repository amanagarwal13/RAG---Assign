# RAG-Powered Multi-Agent Q&A Assistant

A knowledge assistant that retrieves information from documents, generates natural-language answers, and orchestrates its workflow through a basic agentic system.

![RAG-Powered Assistant Demo](https://via.placeholder.com/800x400/151E3F/FFFFFF?text=RAG-Powered+Assistant)

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

![Architecture Diagram](https://mermaid.ink/img/pako:eNp1kc1uwjAQhF_F2lNAJEAgOeSSqgdOvVU99OB4l2Ap_sh2QIjw7nUSEFV7qS3vzHw7Xm8iN05hEmXKCtiuPZw7cM7JtIMvUZRGTpXGJKP9QbRK290sSrTGXYGvBo4ySqbQK9UEaNYWrBvQDt9kbYL1FrQJEQVYeCLjfX6C0sAu5KsUzzk_FvYOsm2DZLXk3HGGvPw9IgOFVEXoEzjPnKCXsW2DrMIJlB1Y4w2NehV-gZbcoeQ19KS-eO4v8fVBdY9a-y2MQ30Djw7ksBLF3mUq5HgG_5WFNXaAyfcCm1bzUMqQGHZitTHsUTXqaThWjGiYRpqAP5h_IrwHJqVoNVgnk5jnfOxH_g3i-YKvDXxP-Z7yLR_7a_zdyHHFZLHmi3XM94v01VU5fgdO2JdN?type=png)

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
   - **LLM Integration**: Uses OpenRouter to generate answers from retrieved context

## Getting Started

### Prerequisites

- Python 3.9+
- Pinecone account (for vector storage)
- OpenRouter account (for LLM access)

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
   OPENROUTER_API_KEY=your_openrouter_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENVIRONMENT=your_pinecone_environment
   PINECONE_INDEX_NAME=rag-agent-index
   LLM_MODEL=mistralai/mistral-7b-instruct
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
│   └── openrouter.py       # OpenRouter API client
│
└── data/                   # Sample documents for ingestion
    ├── company_faq.txt
    ├── product_specs.txt
    └── research_whitepaper.txt
```

## Key Design Choices

1. **Modular Architecture**: Components are decoupled for easy extension and maintenance.
2. **Agent-Based Decision Making**: Queries are routed to specialized tools for optimal handling.
3. **Vector-Based Search**: Semantic search enables finding relevant information even when query terms don't exactly match document content.
4. **Document Chunking Strategy**: Documents are broken into semantic chunks with overlap to maintain context.
5. **LLM Integration**: OpenRouter provides flexibility to use different models while maintaining a consistent API.
6. **Explainable Pipeline**: Each step of the process is transparent and visible to users.

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
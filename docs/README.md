# RAG-Powered Document Q&A System Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [API Documentation](#api-documentation)
6. [Components](#components)
7. [Usage Guide](#usage-guide)
8. [Troubleshooting](#troubleshooting)

## Overview

The RAG-Powered Document Q&A System is a sophisticated question-answering system that uses Retrieval-Augmented Generation (RAG) to provide accurate answers based on document content. The system combines vector search capabilities with large language models to deliver contextually relevant responses.

### Key Features
- Document ingestion and processing
- Semantic search using Pinecone vector store
- OpenAI-powered text generation
- Smart question suggestions
- Real-time query processing
- Comprehensive error handling and logging

## System Architecture

### High-Level Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Web UI     │     │  Flask      │     │  RAG        │
│  (Frontend) │────▶│  Backend    │────▶│  Pipeline   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Document   │     │  Vector     │
                    │  Processor  │     │  Store      │
                    └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  OpenAI     │     │  Pinecone   │
                    │  LLM        │     │  Database   │
                    └─────────────┘     └─────────────┘
```

### Component Interaction
1. User submits a query through the web interface
2. Flask backend processes the request
3. RAG pipeline:
   - Preprocesses the query
   - Searches for relevant documents
   - Generates an answer using the LLM
4. Response is returned to the user

## Installation

### Prerequisites
- Python 3.9 or higher
- Pinecone account
- OpenAI API key

### Setup Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rag-powered-agent.git
   cd rag-powered-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with required API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=rag-agent-index
   EMBEDDING_MODEL=text-embedding-3-large
   ```

## Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| OPENAI_API_KEY | OpenAI API key | Required |
| PINECONE_API_KEY | Pinecone API key | Required |
| PINECONE_INDEX_NAME | Pinecone index name | rag-agent-index |
| EMBEDDING_MODEL | OpenAI embedding model | text-embedding-3-large |

### System Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| MAX_CONTEXT_SNIPPETS | Maximum number of context snippets | 3 |
| MIN_RELEVANCE_SCORE | Minimum relevance score for snippets | 0.5 |
| CHUNK_SIZE | Document chunk size | 300 |
| CHUNK_OVERLAP | Overlap between chunks | 50 |

## API Documentation

### Endpoints

#### 1. Query Processing
- **Endpoint**: `/api/query`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "query": "Your question here"
  }
  ```
- **Response**:
  ```json
  {
    "answer": "Generated answer",
    "context_snippets": [
      {
        "text": "Relevant text snippet",
        "source": "Document name",
        "relevance_score": "0.85"
      }
    ],
    "processing_time": "1.23s"
  }
  ```

#### 2. Document Upload
- **Endpoint**: `/api/documents`
- **Method**: POST
- **Request**: Multipart form data with files
- **Response**:
  ```json
  {
    "success": true,
    "message": "Processed X documents",
    "processed_files": ["file1.txt", "file2.txt"]
  }
  ```

#### 3. System Initialization
- **Endpoint**: `/api/initialize`
- **Method**: POST
- **Response**:
  ```json
  {
    "success": true,
    "message": "Initialized system with X documents",
    "processed_files": ["sample1.txt", "sample2.txt"]
  }
  ```

#### 4. Get Documents
- **Endpoint**: `/api/documents`
- **Method**: GET
- **Response**:
  ```json
  {
    "status": "success",
    "contents": {
      "document1.txt": "content...",
      "document2.txt": "content..."
    }
  }
  ```

#### 5. Get Suggestions
- **Endpoint**: `/api/suggestions`
- **Method**: GET
- **Response**:
  ```json
  {
    "suggestions": [
      {
        "question": "Generated question",
        "context": "Context for the question"
      }
    ]
  }
  ```

## Components

### 1. Document Processor
- Handles document chunking and preprocessing
- Maintains context through overlapping chunks
- Supports multiple document formats
- Implements smart text cleaning

### 2. Vector Store
- Manages document embeddings
- Handles Pinecone integration
- Provides semantic search capabilities
- Supports document deletion and updates

### 3. Document Retriever
- Implements RAG pipeline
- Manages context selection
- Generates answers using LLM
- Handles query preprocessing

## Usage Guide

### Basic Usage
1. Start the application:
   ```bash
   python app.py
   ```

2. Access the web interface:
   ```
   http://localhost:5000
   ```

3. Upload documents:
   - Use the web interface or API
   - Supported formats: .txt files

4. Ask questions:
   - Type your question in the interface
   - View the answer and source context

### Best Practices
1. Document Preparation:
   - Use clear, well-structured text
   - Avoid special characters
   - Keep documents focused on specific topics

2. Query Formulation:
   - Be specific and clear
   - Use natural language
   - Avoid ambiguous terms

3. System Maintenance:
   - Regular document updates
   - Monitor system logs
   - Check API rate limits

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check API keys in .env file
   - Verify internet connection
   - Check API rate limits

2. **Document Processing Issues**
   - Verify file format
   - Check file encoding
   - Ensure file size is reasonable

3. **Search Quality Issues**
   - Adjust chunk size
   - Modify relevance threshold
   - Update document content

### Logging
- Logs are available in the application logs
- Set logging level in configuration
- Monitor for error messages

### Support
For additional support:
- Check the GitHub repository
- Submit issues on GitHub
- Contact: amannagarwal13@gmail.com 
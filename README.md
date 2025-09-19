# RAG Tracer: Tracing & Hallucination Detection System

A comprehensive tracing system for Retrieval-Augmented Generation (RAG) pipelines with hallucination detection capabilities. This system allows you to monitor, analyze, and detect hallucinations in any RAG application using OpenAI or Hugging Face models.

## Features

- **Full Pipeline Tracing**: Track all stages of your RAG pipeline (prompt construction, embeddings, retrieval, model response)
- **Hallucination Detection**: Automatically detect hallucinations via retrieval-grounding checks using RoBERTa-MNLI entailment classifier
- **Hybrid Storage**: Store structured metadata in PostgreSQL with SQLAlchemy ORM, and vector data/embeddings/logs in MinIO/S3
- **Real-time Monitoring**: REST API + WebSocket support for real-time trace ingestion
- **Visualization Dashboard**: React-based frontend dashboard with charts and visualizations
- **Containerized Deployment**: Fully containerized with Docker Compose for easy deployment
- **Python SDK**: Simple Python client SDK for instrumenting any RAG application

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌──────────────────┐
│   RAG App       │───▶│  Tracer SDK  │───▶│  FastAPI Server  │
│ (Instrumented)  │    │              │    │                  │
└─────────────────┘    └──────────────┘    │  ┌─────────────┐ │
                                           │  │ REST API    │ │
                                           │  └─────────────┘ │
                                           │  ┌─────────────┐ │
                                           │  │ WebSocket   │ │
                                           │  └─────────────┘ │
                                           └─────────┬────────┘
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────▼────────┐
│   PostgreSQL    │◀───│   Celery     │◀───│   MinIO/S3       │
│ (Structured     │    │ (Worker)     │    │ (Vector data,    │
│  metadata)      │    │              │    │  embeddings,     │
│                 │    │              │    │  logs)           │
└─────────────────┘    └──────────────┘    └──────────────────┘
                                                     │
┌─────────────────┐                                  │
│   Dashboard     │◀─────────────────────────────────┘
│ (React frontend)│
└─────────────────┘
```

## Components

### 1. Tracer SDK (`tracer_sdk/`)

A Python client library for instrumenting RAG applications with tracing capabilities.

- Simple API for tracing all stages of a RAG pipeline
- Async mode for non-blocking trace submission
- WebSocket support for real-time monitoring

### 2. FastAPI Server (`api/`)

The core tracing server with REST and WebSocket endpoints.

- PostgreSQL storage with SQLAlchemy ORM
- MinIO integration for vector data and logs
- Prometheus metrics endpoint for monitoring
- Structured data models for all trace components

### 3. Worker Service (`workers/`)

Background service for hallucination detection.

- Uses RoBERTa-MNLI entailment classifier
- Checks if response sentences are supported by retrieved documents
- Computes groundedness scores
- Stores hallucination check results

### 4. Dashboard (`dashboard/`)

React-based visualization dashboard.

- Charts for latency breakdowns
- Groundedness score distributions
- Token usage tracking
- Detailed trace views

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd rag_tracer
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the components**:
   - FastAPI Server: http://localhost:8000
   - Dashboard: http://localhost:8080
   - MinIO: http://localhost:9000
   - PostgreSQL: localhost:5432
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

## API Endpoints

### REST API

- `POST /traces/` - Create a new trace
- `GET /traces/{prompt_id}` - Get trace by ID

### WebSocket API

- `ws://localhost:8000/ws/traces` - Real-time trace submission

## Data Models

### Trace Structure

```json
{
  "user_query": "string",
  "system_prompt": "string (optional)",
  "final_prompt": "string",
  "embedding": {
    "vector": "[float]",
    "retrieval_candidates": "[{doc_id, score}] (optional)"
  },
  "retrievals": [
    {
      "document_id": "string",
      "similarity_score": "float",
      "metadata": "object (optional)"
    }
  ],
  "response": {
    "text": "string",
    "token_stream": "[string] (optional)",
    "hallucination_check": {
      "groundedness_score": "float",
      "unsupported_sentences": "[string] (optional)",
      "entailment_results": "object (optional)"
    }
  },
  "telemetry": {
    "embedding_latency_ms": "float (optional)",
    "retrieval_latency_ms": "float (optional)",
    "llm_latency_ms": "float (optional)",
    "total_latency_ms": "float (optional)",
    "embedding_tokens": "integer (optional)",
    "completion_tokens": "integer (optional)",
    "api_cost": "float (optional)"
  }
}
```

## Example Usage

See the example notebook in `notebooks/rag_tracer_example.ipynb` for a complete integration example with OpenAI and pgvector.

### Simple Test

You can test the tracer functionality with the provided test script:

```bash
python test_tracer.py
```

This script demonstrates both synchronous and asynchronous tracing without requiring external API keys.

### Basic Integration

```python
from tracer_sdk.tracer import RAGTracer, EmbeddingData, RetrievalData, ResponseData, TelemetryData

# Initialize tracer
tracer = RAGTracer(api_url="http://localhost:8000")

# Trace a RAG pipeline execution
result = tracer.trace_complete(
    user_query="Who is CEO of Tesla?",
    system_prompt="You are a helpful assistant.",
    final_prompt="Context: Elon Musk is CEO of Tesla. Question: Who is CEO of Tesla?",
    embedding=EmbeddingData(
        vector=[0.1, 0.2, 0.3, 0.4, 0.5],  # Your embedding vector
        retrieval_candidates=[{"doc_id": "doc1", "score": 0.95}]
    ),
    retrievals=[
        RetrievalData(
            document_id="doc1",
            similarity_score=0.95,
            metadata={"title": "Tesla Leadership", "text": "Elon Musk is CEO of Tesla"}
        )
    ],
    response=ResponseData(
        text="The current CEO of Tesla is Elon Musk.",
        token_stream=["The", "current", "CEO", "of", "Tesla", "is", "Elon", "Musk", "."]
    ),
    telemetry=TelemetryData(
        embedding_latency_ms=50.0,
        retrieval_latency_ms=80.0,
        llm_latency_ms=950.0,
        total_latency_ms=1080.0,
        embedding_tokens=10,
        completion_tokens=45,
        api_cost=0.0015
    )
)
```

## Monitoring

The system exposes Prometheus metrics at `/metrics` endpoint. Grafana dashboards are pre-configured to visualize these metrics.

## Storage

- **PostgreSQL**: Structured trace metadata
- **MinIO**: Vector embeddings, retrieval candidates, and detailed logs
- **pgvector**: Vector similarity search capabilities

## Development

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 18+ (for dashboard development)

### Backend Development

1. Install Python dependencies:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Worker Development

1. Install worker dependencies:
   ```bash
   cd workers
   pip install -r requirements.txt
   ```

2. Run the Celery worker:
   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```

### Dashboard Development

1. Install Node dependencies:
   ```bash
   cd dashboard
   npm install
   ```

2. Run the development server:
   ```bash
   npm start
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.

# RAG Tracer SDK

Python client library for instrumenting RAG applications with tracing and hallucination detection.

## Installation

```bash
pip install rag-tracer-sdk
```

Or install directly from source:

```bash
pip install -e .
```

## Usage

### Basic Usage

```python
from tracer_sdk.tracer import RAGTracer, EmbeddingData, RetrievalData, ResponseData, TelemetryData

# Initialize the tracer
tracer = RAGTracer(api_url="http://localhost:8000")

# Trace a complete RAG pipeline
result = tracer.trace_complete(
    user_query="Who is CEO of Tesla?",
    system_prompt="You are a helpful assistant.",
    final_prompt="Context: Elon Musk is CEO of Tesla. Question: Who is CEO of Tesla?",
    embedding=EmbeddingData(
        vector=[0.1, 0.2, 0.3, ...],  # Your embedding vector
        retrieval_candidates=[
            {"doc_id": "doc1", "score": 0.95},
            {"doc_id": "doc2", "score": 0.87}
        ]
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

print(result)
```

### Asynchronous Mode

For non-blocking tracing:

```python
# Initialize tracer in async mode
tracer = RAGTracer(api_url="http://localhost:8000", async_mode=True)

# Trace will return immediately
result = tracer.trace_complete(...)
```

## API Reference

### RAGTracer

Main class for tracing RAG applications.

#### `__init__(api_url: str = "http://localhost:8000", async_mode: bool = False)`

Initialize the tracer.

- `api_url`: URL of the tracing API server
- `async_mode`: Whether to send traces asynchronously

#### `trace_complete(...)`

Trace a complete RAG pipeline execution.

#### `trace_prompt(...)`

Trace prompt construction phase.

#### `trace_embedding(...)`

Trace embedding generation phase.

#### `trace_retrieval(...)`

Trace document retrieval phase.

#### `trace_response(...)`

Trace model response phase.

## Data Classes

### EmbeddingData
- `vector`: List of floats representing the embedding
- `retrieval_candidates`: Optional list of candidate documents with scores

### RetrievalData
- `document_id`: String identifier for the document
- `similarity_score`: Float similarity score
- `metadata`: Optional dictionary with document metadata

### ResponseData
- `text`: String response from the model
- `token_stream`: Optional list of tokens
- `hallucination_check`: Optional hallucination check data

### TelemetryData
- `embedding_latency_ms`: Embedding generation time
- `retrieval_latency_ms`: Document retrieval time
- `llm_latency_ms`: Language model response time
- `total_latency_ms`: Total pipeline time
- `embedding_tokens`: Number of tokens used for embedding
- `completion_tokens`: Number of tokens in completion
- `api_cost`: Cost of API calls
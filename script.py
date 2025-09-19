from tracer_sdk.tracer import RAGTracer, EmbeddingData, RetrievalData, ResponseData, TelemetryData

# Initialize tracer
tracer = RAGTracer(api_url="http://rag_tracer-dashboard-1:8080")
print("initialized")
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
from tracer_sdk.tracer import RAGTracer, EmbeddingData, RetrievalData, ResponseData, TelemetryData

# Initialize tracer
tracer = RAGTracer(api_url="http://localhost:8000")
print("Tracer initialized")

# Simple test without external dependencies
def test_simple_trace():
    print("Testing simple trace...")
    
    # Trace a RAG pipeline execution
    result = tracer.trace_complete(
        user_query="Who is CEO of Tesla?",
        system_prompt="You are a helpful assistant.",
        final_prompt="Context: Elon Musk is CEO of Tesla. Question: Who is CEO of Tesla?",
        embedding=EmbeddingData(
            vector=[0.1, 0.2, 0.3, 0.4, 0.5],  # Simple embedding vector
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
            token_stream=["The", "current", "CEO", "of", "Tesla", "is", "Elon", "Musk", "."],
            hallucination_check=None
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
    
    print("Trace result:", result)
    return result

# Test async mode
def test_async_trace():
    print("Testing async trace...")
    
    # Initialize async tracer
    async_tracer = RAGTracer(api_url="http://localhost:8000", async_mode=True)
    
    # Trace a RAG pipeline execution (async)
    result = async_tracer.trace_complete(
        user_query="Who is CEO of SpaceX?",
        system_prompt="You are a helpful assistant.",
        final_prompt="Context: Elon Musk is CEO of SpaceX. Question: Who is CEO of SpaceX?",
        embedding=EmbeddingData(
            vector=[0.2, 0.3, 0.4, 0.5, 0.6],  # Simple embedding vector
            retrieval_candidates=[{"doc_id": "doc2", "score": 0.92}]
        ),
        retrievals=[
            RetrievalData(
                document_id="doc2",
                similarity_score=0.92,
                metadata={"title": "SpaceX Leadership", "text": "Elon Musk is CEO of SpaceX"}
            )
        ],
        response=ResponseData(
            text="The current CEO of SpaceX is Elon Musk.",
            token_stream=["The", "current", "CEO", "of", "SpaceX", "is", "Elon", "Musk", "."],
            hallucination_check=None
        ),
        telemetry=TelemetryData(
            embedding_latency_ms=45.0,
            retrieval_latency_ms=75.0,
            llm_latency_ms=920.0,
            total_latency_ms=1040.0,
            embedding_tokens=10,
            completion_tokens=42,
            api_cost=0.0014
        )
    )
    
    print("Async trace result:", result)
    return result

if __name__ == "__main__":
    # Test simple trace
    test_simple_trace()
    
    # Test async trace
    test_async_trace()
    
    print("All tests completed!")
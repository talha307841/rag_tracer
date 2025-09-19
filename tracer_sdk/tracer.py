import requests
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from threading import Thread


@dataclass
class EmbeddingData:
    vector: List[float]
    retrieval_candidates: Optional[List[Dict[str, Any]]] = None


@dataclass
class RetrievalData:
    document_id: str
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class HallucinationCheckData:
    groundedness_score: float
    unsupported_sentences: Optional[List[str]] = None
    entailment_results: Optional[List[Dict[str, Any]]] = None


@dataclass
class ResponseData:
    text: str
    token_stream: Optional[List[str]] = None
    hallucination_check: Optional[HallucinationCheckData] = None


@dataclass
class TelemetryData:
    embedding_latency_ms: Optional[float] = None
    retrieval_latency_ms: Optional[float] = None
    llm_latency_ms: Optional[float] = None
    total_latency_ms: Optional[float] = None
    embedding_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    api_cost: Optional[float] = None


class RAGTracer:
    def __init__(self, api_url: str = "http://localhost:8000", async_mode: bool = False):
        """
        Initialize the RAG Tracer client.
        
        Args:
            api_url: URL of the tracing API server
            async_mode: Whether to send traces asynchronously
        """
        self.api_url = api_url.rstrip("/")
        self.async_mode = async_mode
        self.session = requests.Session()

    def trace_complete(
        self,
        user_query: str,
        final_prompt: str,
        embedding: EmbeddingData,
        retrievals: List[RetrievalData],
        response: ResponseData,
        system_prompt: Optional[str] = None,
        telemetry: Optional[TelemetryData] = None
    ) -> Dict[str, Any]:
        """
        Trace a complete RAG pipeline execution.
        
        Args:
            user_query: Original user query
            system_prompt: System prompt used (optional)
            final_prompt: Final prompt sent to the model
            embedding: Embedding data with vector and candidates
            retrievals: List of retrieved documents
            response: Model response with optional hallucination check
            telemetry: Performance and cost metrics
            
        Returns:
            API response with trace data
        """
        trace_data = {
            "user_query": user_query,
            "system_prompt": system_prompt,
            "final_prompt": final_prompt,
            "embedding": asdict(embedding),
            "retrievals": [asdict(r) for r in retrievals],
            "response": asdict(response),
            "telemetry": asdict(telemetry) if telemetry else {}
        }

        if self.async_mode:
            thread = Thread(target=self._send_trace, args=(trace_data,))
            thread.start()
            return {"status": "submitted_async"}
        else:
            return self._send_trace(trace_data)

    def _send_trace(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send trace data to the API."""
        try:
            response = self.session.post(
                f"{self.api_url}/traces/",
                json=trace_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def trace_prompt(
        self,
        user_query: str,
        final_prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Trace prompt construction phase.
        
        Args:
            user_query: Original user query
            system_prompt: System prompt used (optional)
            final_prompt: Final prompt sent to the model
            
        Returns:
            API response
        """
        # In a more complete implementation, this would create a partial trace
        # For now, we'll just use trace_complete with minimal data
        return self.trace_complete(
            user_query=user_query,
            system_prompt=system_prompt,
            final_prompt=final_prompt,
            embedding=EmbeddingData(vector=[]),
            retrievals=[],
            response=ResponseData(text=""),
            telemetry=TelemetryData()
        )

    def trace_embedding(
        self,
        vector: List[float],
        retrieval_candidates: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Trace embedding generation phase.
        
        Args:
            vector: Embedding vector
            retrieval_candidates: Candidate documents with similarity scores
            
        Returns:
            API response
        """
        # This would typically be used in conjunction with other trace methods
        # For now, we'll just return a placeholder
        return {"status": "embedding_traced", "vector_length": len(vector)}

    def trace_retrieval(
        self,
        retrievals: List[RetrievalData]
    ) -> Dict[str, Any]:
        """
        Trace document retrieval phase.
        
        Args:
            retrievals: List of retrieved documents
            
        Returns:
            API response
        """
        # This would typically be used in conjunction with other trace methods
        # For now, we'll just return a placeholder
        return {"status": "retrieval_traced", "document_count": len(retrievals)}

    def trace_response(
        self,
        text: str,
        token_stream: Optional[List[str]] = None,
        hallucination_check: Optional[HallucinationCheckData] = None
    ) -> Dict[str, Any]:
        """
        Trace model response phase.
        
        Args:
            text: Model response text
            token_stream: Token-by-token stream (optional)
            hallucination_check: Hallucination check results (optional)
            
        Returns:
            API response
        """
        # This would typically be used in conjunction with other trace methods
        # For now, we'll just return a placeholder
        return {"status": "response_traced", "response_length": len(text)}
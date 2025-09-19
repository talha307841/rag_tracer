from pydantic import BaseModel, Field
from typing import List, Optional, Any

class EmbeddingIn(BaseModel):
    vector: List[float]
    retrieval_candidates: Optional[List[Any]] = None

class RetrievalIn(BaseModel):
    document_id: str
    similarity_score: float
    metadata: Optional[Any] = None

class HallucinationCheckIn(BaseModel):
    groundedness_score: float
    unsupported_sentences: Optional[List[str]] = None
    entailment_results: Optional[Any] = None

class ResponseIn(BaseModel):
    text: str
    token_stream: Optional[List[str]] = None
    hallucination_check: Optional[HallucinationCheckIn] = None

class TelemetryIn(BaseModel):
    embedding_latency_ms: Optional[float] = None
    retrieval_latency_ms: Optional[float] = None
    llm_latency_ms: Optional[float] = None
    total_latency_ms: Optional[float] = None
    embedding_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    api_cost: Optional[float] = None

class TraceIn(BaseModel):
    user_query: str
    system_prompt: Optional[str] = None
    final_prompt: str
    embedding: EmbeddingIn
    retrievals: List[RetrievalIn]
    response: ResponseIn
    telemetry: TelemetryIn
    # MinIO storage fields
    store_embedding_dump: Optional[bool] = False
    store_retrieval_logs: Optional[bool] = False
    store_response_logs: Optional[bool] = False
</content>
</file>

# Output Schemas
class HallucinationCheckOut(HallucinationCheckIn):
    id: int
    class Config:
        orm_mode = True

class ResponseOut(ResponseIn):
    id: int
    hallucination_checks: Optional[List[HallucinationCheckOut]] = None
    class Config:
        orm_mode = True

class RetrievalOut(RetrievalIn):
    id: int
    class Config:
        orm_mode = True

class EmbeddingOut(EmbeddingIn):
    id: int
    class Config:
        orm_mode = True

class TelemetryOut(TelemetryIn):
    id: int
    class Config:
        orm_mode = True

class TraceOut(BaseModel):
    id: int
    user_query: str
    system_prompt: Optional[str]
    final_prompt: str
    embeddings: List[EmbeddingOut]
    retrievals: List[RetrievalOut]
    responses: List[ResponseOut]
    telemetry: Optional[TelemetryOut]
    class Config:
        orm_mode = True

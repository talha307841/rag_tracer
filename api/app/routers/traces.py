from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ..core.database import get_db
from ..models import tracing
from ..schemas import traces as schemas
from ..core import minio_utils

router = APIRouter(prefix="/traces", tags=["traces"])

@router.post("/", response_model=schemas.TraceOut)
def create_trace(trace: schemas.TraceIn, db: Session = Depends(get_db)):
    # Create Prompt
    prompt = tracing.Prompt(
        user_query=trace.user_query,
        system_prompt=trace.system_prompt,
        final_prompt=trace.final_prompt
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    # Add Embedding
    embedding = tracing.Embedding(
        vector=trace.embedding.vector,
        prompt_id=prompt.id,
        retrieval_candidates=trace.embedding.retrieval_candidates
    )
    db.add(embedding)
    db.commit()
    db.refresh(embedding)
    # Add Retrievals
    for r in trace.retrievals:
        retrieval = tracing.Retrieval(
            prompt_id=prompt.id,
            document_id=r.document_id,
            similarity_score=r.similarity_score,
            metadata=r.metadata
        )
        db.add(retrieval)
    db.commit()
    # Add Response
    response = tracing.Response(
        prompt_id=prompt.id,
        text=trace.response.text,
        token_stream=trace.response.token_stream
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    # Add HallucinationCheck
    if trace.response.hallucination_check:
        hc = trace.response.hallucination_check
        hallucination = tracing.HallucinationCheck(
            response_id=response.id,
            groundedness_score=hc.groundedness_score,
            unsupported_sentences=hc.unsupported_sentences,
            entailment_results=hc.entailment_results
        )
        db.add(hallucination)
        db.commit()
    # Add Telemetry
    telemetry = tracing.Telemetry(
        prompt_id=prompt.id,
        embedding_latency_ms=trace.telemetry.embedding_latency_ms,
        retrieval_latency_ms=trace.telemetry.retrieval_latency_ms,
        llm_latency_ms=trace.telemetry.llm_latency_ms,
        total_latency_ms=trace.telemetry.total_latency_ms,
        embedding_tokens=trace.telemetry.embedding_tokens,
        completion_tokens=trace.telemetry.completion_tokens,
        api_cost=trace.telemetry.api_cost
    )
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    
    # Store data in MinIO if requested
    if trace.store_embedding_dump:
        embedding_data = {
            "prompt_id": prompt.id,
            "vector": trace.embedding.vector,
            "retrieval_candidates": trace.embedding.retrieval_candidates
        }
        minio_utils.upload_data(
            "embeddings",
            f"embedding_{prompt.id}.json",
            json.dumps(embedding_data).encode('utf-8'),
            "application/json"
        )
    
    if trace.store_retrieval_logs:
        retrieval_data = [
            {
                "document_id": r.document_id,
                "similarity_score": r.similarity_score,
                "metadata": r.metadata
            }
            for r in trace.retrievals
        ]
        minio_utils.upload_data(
            "retrievals",
            f"retrieval_{prompt.id}.json",
            json.dumps(retrieval_data).encode('utf-8'),
            "application/json"
        )
    
    if trace.store_response_logs:
        response_data = {
            "prompt_id": prompt.id,
            "text": trace.response.text,
            "token_stream": trace.response.token_stream,
            "hallucination_check": trace.response.hallucination_check
        }
        minio_utils.upload_data(
            "responses",
            f"response_{prompt.id}.json",
            json.dumps(response_data).encode('utf-8'),
            "application/json"
        )
    
    return schemas.TraceOut.from_orm(prompt)

@router.get("/{prompt_id}", response_model=schemas.TraceOut)
def get_trace(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(tracing.Prompt).filter(tracing.Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Trace not found")
    return schemas.TraceOut.from_orm(prompt)

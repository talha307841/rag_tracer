import os
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.app.models import tracing
from api.app.core.database import Base
from minio import Minio
from transformers import pipeline

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/rag_tracer")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

celery_app = Celery('worker', broker=CELERY_BROKER_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Load entailment pipeline (RoBERTa-MNLI)
entailment_pipe = pipeline("text-classification", model="roberta-large-mnli")

@celery_app.task
def check_hallucination(response_id: int):
    db = SessionLocal()
    response = db.query(tracing.Response).filter(tracing.Response.id == response_id).first()
    if not response:
        db.close()
        return
    # Retrieve associated prompt and retrievals
    prompt = response.prompt
    retrievals = db.query(tracing.Retrieval).filter(tracing.Retrieval.prompt_id == prompt.id).all()
    retrieved_texts = [r.metadata.get("text", "") for r in retrievals if r.metadata]
    # Split response into sentences
    sentences = response.text.split('.')
    supported = 0
    entailment_results = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        # Check entailment against all retrieved docs
        is_supported = False
        for doc in retrieved_texts:
            result = entailment_pipe(f"{sent} </s></s> {doc}")[0]
            entailment_results.append({"sentence": sent, "doc": doc, "label": result["label"], "score": result["score"]})
            if result["label"] == "ENTAILMENT" and result["score"] > 0.7:
                is_supported = True
                break
        if is_supported:
            supported += 1
    groundedness = supported / max(1, len(sentences))
    unsupported_sentences = [e["sentence"] for e in entailment_results if e["label"] != "ENTAILMENT"]
    # Store hallucination check
    hallucination = tracing.HallucinationCheck(
        response_id=response.id,
        groundedness_score=groundedness,
        unsupported_sentences=unsupported_sentences,
        entailment_results=entailment_results
    )
    db.add(hallucination)
    db.commit()
    db.close()
    return groundedness

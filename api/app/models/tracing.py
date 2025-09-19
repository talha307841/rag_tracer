from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from ..core.database import Base

class Prompt(Base):
    __tablename__ = 'prompts'
    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(String, nullable=False)
    system_prompt = Column(String, nullable=True)
    final_prompt = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    embeddings = relationship("Embedding", back_populates="prompt", cascade="all, delete-orphan")
    retrievals = relationship("Retrieval", back_populates="prompt", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="prompt", cascade="all, delete-orphan")
    telemetry = relationship("Telemetry", back_populates="prompt", uselist=False, cascade="all, delete-orphan")

class Embedding(Base):
    __tablename__ = 'embeddings'
    id = Column(Integer, primary_key=True, index=True)
    vector = Column(Vector(1536), nullable=False)
    prompt_id = Column(Integer, ForeignKey('prompts.id'), nullable=False)
    retrieval_candidates = Column(JSON, nullable=True)  # [{doc_id, score}, ...]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prompt = relationship("Prompt", back_populates="embeddings")

class Retrieval(Base):
    __tablename__ = 'retrievals'
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey('prompts.id'), nullable=False)
    document_id = Column(String, nullable=False)
    similarity_score = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prompt = relationship("Prompt", back_populates="retrievals")

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey('prompts.id'), nullable=False)
    text = Column(String, nullable=False)
    token_stream = Column(JSON, nullable=True)  # List of tokens
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prompt = relationship("Prompt", back_populates="responses")
    hallucination_checks = relationship("HallucinationCheck", back_populates="response", cascade="all, delete-orphan")

class HallucinationCheck(Base):
    __tablename__ = 'hallucination_checks'
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey('responses.id'), nullable=False)
    groundedness_score = Column(Float, nullable=False)
    unsupported_sentences = Column(JSON, nullable=True)  # List of unsupported sentences
    entailment_results = Column(JSON, nullable=True)  # Sentence-level entailment
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    response = relationship("Response", back_populates="hallucination_checks")

class Telemetry(Base):
    __tablename__ = 'telemetry'
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey('prompts.id'), nullable=False)
    embedding_latency_ms = Column(Float, nullable=True)
    retrieval_latency_ms = Column(Float, nullable=True)
    llm_latency_ms = Column(Float, nullable=True)
    total_latency_ms = Column(Float, nullable=True)
    embedding_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    api_cost = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prompt = relationship("Prompt", back_populates="telemetry")

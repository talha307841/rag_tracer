import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import axios from 'axios';
import './TraceDetail.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function TraceDetail() {
  const { id } = useParams();
  const [trace, setTrace] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTrace();
  }, [id]);

  const fetchTrace = async () => {
    try {
      const response = await axios.get(`${API_URL}/traces/${id}`);
      setTrace(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch trace');
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!trace) return <div className="error">Trace not found</div>;

  // Prepare retrieval data for chart
  const retrievalData = trace.retrievals.map((retrieval, index) => ({
    name: `Doc ${index + 1}`,
    score: retrieval.similarity_score
  }));

  // Prepare token stream data
  const tokenStream = trace.responses[0]?.token_stream || [];
  const tokenData = tokenStream.map((token, index) => ({
    index,
    token
  }));

  return (
    <div className="trace-detail">
      <h1>Trace Detail</h1>
      <Link to="/" className="back-link">← Back to Dashboard</Link>
      
      <div className="trace-section">
        <h2>Prompt Information</h2>
        <div className="prompt-info">
          <p><strong>User Query:</strong> {trace.user_query}</p>
          <p><strong>System Prompt:</strong> {trace.system_prompt || 'N/A'}</p>
          <p><strong>Final Prompt:</strong> {trace.final_prompt}</p>
        </div>
      </div>

      <div className="trace-section">
        <h2>Retrieval Results</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={retrievalData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="score" fill="#8884d8" name="Similarity Score" />
          </BarChart>
        </ResponsiveContainer>
        
        <div className="retrievals-list">
          {trace.retrievals.map((retrieval, index) => (
            <div key={index} className="retrieval-item">
              <h3>Document {index + 1}</h3>
              <p><strong>ID:</strong> {retrieval.document_id}</p>
              <p><strong>Similarity Score:</strong> {retrieval.similarity_score.toFixed(4)}</p>
              <p><strong>Metadata:</strong> {JSON.stringify(retrieval.metadata)}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="trace-section">
        <h2>Model Response</h2>
        <div className="response-info">
          <p><strong>Text:</strong> {trace.responses[0]?.text}</p>
          <p><strong>Groundedness Score:</strong> {trace.responses[0]?.hallucination_checks[0]?.groundedness_score?.toFixed(2) || 'N/A'}</p>
        </div>
        
        <h3>Token Stream</h3>
        <div className="token-stream">
          {tokenData.map((item) => (
            <span key={item.index} className="token">{item.token}</span>
          ))}
        </div>
      </div>

      <div className="trace-section">
        <h2>Telemetry</h2>
        <div className="telemetry-info">
          <p><strong>Embedding Latency:</strong> {trace.telemetry?.embedding_latency_ms?.toFixed(2) || 'N/A'} ms</p>
          <p><strong>Retrieval Latency:</strong> {trace.telemetry?.retrieval_latency_ms?.toFixed(2) || 'N/A'} ms</p>
          <p><strong>LLM Latency:</strong> {trace.telemetry?.llm_latency_ms?.toFixed(2) || 'N/A'} ms</p>
          <p><strong>Total Latency:</strong> {trace.telemetry?.total_latency_ms?.toFixed(2) || 'N/A'} ms</p>
          <p><strong>Embedding Tokens:</strong> {trace.telemetry?.embedding_tokens || 'N/A'}</p>
          <p><strong>Completion Tokens:</strong> {trace.telemetry?.completion_tokens || 'N/A'}</p>
          <p><strong>API Cost:</strong> ${trace.telemetry?.api_cost?.toFixed(6) || 'N/A'}</p>
        </div>
      </div>
    </div>
  );
}

export default TraceDetail;
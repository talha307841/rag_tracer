import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  LineChart, Line, BarChart, Bar, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import axios from 'axios';
import './Dashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Dashboard() {
  const [traces, setTraces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTraces();
  }, []);

  const fetchTraces = async () => {
    try {
      const response = await axios.get(`${API_URL}/traces`);
      setTraces(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch traces');
      setLoading(false);
    }
  };

  // Prepare data for charts
  const latencyData = traces.map(trace => ({
    id: trace.id,
    retrieval: trace.telemetry?.retrieval_latency_ms || 0,
    llm: trace.telemetry?.llm_latency_ms || 0,
    total: trace.telemetry?.total_latency_ms || 0
  }));

  const groundednessData = traces.map(trace => ({
    id: trace.id,
    groundedness: trace.responses[0]?.hallucination_checks[0]?.groundedness_score || 0
  }));

  const tokenData = traces.map(trace => ({
    id: trace.id,
    embedding: trace.telemetry?.embedding_tokens || 0,
    completion: trace.telemetry?.completion_tokens || 0
  }));

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard">
      <h1>RAG Tracer Dashboard</h1>
      
      <div className="charts-container">
        <div className="chart-card">
          <h2>Latency Breakdown (ms)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={latencyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="id" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="retrieval" fill="#8884d8" name="Retrieval" />
              <Bar dataKey="llm" fill="#82ca9d" name="LLM" />
              <Bar dataKey="total" fill="#ffc658" name="Total" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>Groundedness Score</h2>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={groundednessData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="id" name="Trace ID" />
              <YAxis dataKey="groundedness" name="Groundedness" domain={[0, 1]} />
              <Tooltip />
              <Scatter name="Groundedness" dataKey="groundedness" fill="#ff7300" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>Token Usage</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={tokenData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="id" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="embedding" stroke="#8884d8" name="Embedding Tokens" />
              <Line type="monotone" dataKey="completion" stroke="#82ca9d" name="Completion Tokens" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="traces-list">
        <h2>Recent Traces</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>User Query</th>
              <th>System Prompt</th>
              <th>Final Prompt</th>
              <th>Response</th>
              <th>Groundedness</th>
              <th>Total Latency (ms)</th>
            </tr>
          </thead>
          <tbody>
            {traces.map(trace => (
              <tr key={trace.id}>
                <td><Link to={`/trace/${trace.id}`}>{trace.id}</Link></td>
                <td>{trace.user_query}</td>
                <td>{trace.system_prompt || 'N/A'}</td>
                <td>{trace.final_prompt}</td>
                <td>{trace.responses[0]?.text || 'N/A'}</td>
                <td>{trace.responses[0]?.hallucination_checks[0]?.groundedness_score?.toFixed(2) || 'N/A'}</td>
                <td>{trace.telemetry?.total_latency_ms?.toFixed(2) || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;
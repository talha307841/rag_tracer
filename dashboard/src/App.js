import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import TraceDetail from './components/TraceDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <Link to="/">RAG Tracer Dashboard</Link>
          </div>
          <ul className="nav-links">
            <li><Link to="/">Dashboard</Link></li>
          </ul>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/trace/:id" element={<TraceDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
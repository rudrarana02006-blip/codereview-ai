import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { formatDistanceToNow } from 'date-fns';
import {
  Code,
  Send,
  Loader2,
  AlertTriangle,
  Lightbulb,
  CheckCircle,
  Copy,
  Download,
  Clock,
  Menu,
  FileText
} from 'lucide-react';

// Types
interface Risk {
  description: string;
  severity: 'low' | 'medium' | 'high';
}

interface Suggestion {
  description: string;
  line_reference: string | null;
}

interface Review {
  id: number;
  raw_input: string;
  summary: string;
  overall_rating: string;
  created_at: string;
  risks: Risk[];
  suggestions: Suggestion[];
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

function App() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentReview, setCurrentReview] = useState<Review | null>(null);
  const [history, setHistory] = useState<Review[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/reviews`);
      setHistory(res.data);
    } catch (err) {
      console.error('Failed to fetch history', err);
    }
  };

  const handleReview = async () => {
    if (!input.trim()) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE}/review`, { raw_input: input });
      setCurrentReview(res.data);
      fetchHistory(); // Refresh history
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate review. Ensure Ollama is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadReview = async (id: number) => {
    try {
      const res = await axios.get(`${API_BASE}/reviews/${id}`);
      setCurrentReview(res.data);
      setInput(res.data.raw_input);
    } catch (err) {
      console.error('Failed to load review', err);
    }
  };

  const copyToClipboard = () => {
    if (!currentReview) return;
    const text = `
## Code Review Summary
${currentReview.summary}

## Rating
${currentReview.overall_rating}

## Risks
${currentReview.risks.map(r => `- [${r.severity.toUpperCase()}] ${r.description}`).join('\n')}

## Suggestions
${currentReview.suggestions.map(s => `- ${s.description} ${s.line_reference ? `(Line: ${s.line_reference})` : ''}`).join('\n')}
    `.trim();
    
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const getRatingClass = (rating: string) => {
    const l = rating.toLowerCase();
    if (l.includes('good')) return 'rating-looks-good';
    if (l.includes('major')) return 'rating-needs-major';
    return 'rating-needs-minor';
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1><img src="/favicon.svg" alt="CodeReview AI Logo" style={{ width: '28px', height: '28px' }} /> <span>CodeReview AI</span></h1>
        </div>
        <div className="history-list">
          {history.length === 0 ? (
            <div className="empty-state" style={{ height: 'auto', padding: '2rem' }}>
              <Clock size={24} />
              <p>No past reviews</p>
            </div>
          ) : (
            history.map((rev) => (
              <div 
                key={rev.id} 
                className={`history-item ${currentReview?.id === rev.id ? 'active' : ''}`}
                onClick={() => loadReview(rev.id)}
              >
                <div className="history-item-date">
                  {formatDistanceToNow(new Date(rev.created_at), { addSuffix: true })}
                </div>
                <div className="history-item-summary">{rev.summary}</div>
                <div className="history-item-rating">{rev.overall_rating.split('-')[0]}</div>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <div className="header-actions">
          <h2>New Code Review</h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {currentReview && (
              <button className="btn" onClick={copyToClipboard}>
                <Copy size={16} /> Copy Markdown
              </button>
            )}
          </div>
        </div>

        <div className="input-section">
          <textarea
            className="input-area"
            placeholder="Paste your git diff, PR description, or code block here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          ></textarea>
          
          <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '1rem' }}>
            {error && <span style={{ color: 'var(--severity-high)' }}>{error}</span>}
            <button 
              className="btn btn-primary" 
              onClick={handleReview}
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
              {isLoading ? 'Analyzing...' : 'Analyze Code'}
            </button>
          </div>
        </div>

        {currentReview ? (
          <div className="review-output">
            {/* Rating & Summary */}
            <div className="card">
              <h2><FileText size={20} /> Overview</h2>
              <div style={{ marginBottom: '1rem' }}>
                <span className={`rating-badge ${getRatingClass(currentReview.overall_rating)}`}>
                  {currentReview.overall_rating}
                </span>
              </div>
              <p className="summary-text">{currentReview.summary}</p>
            </div>

            {/* Risks */}
            <div className="card">
              <h2><AlertTriangle size={20} color="var(--severity-high)" /> Risk Flags</h2>
              {currentReview.risks.length > 0 ? (
                <div className="item-list">
                  {currentReview.risks.map((risk, i) => (
                    <div key={i} className={`list-item severity-${risk.severity}`}>
                      <div className="item-header">
                        <span className="item-description">{risk.description}</span>
                        <span className={`severity-badge ${risk.severity}`}>{risk.severity}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--severity-low)' }}>No significant risks identified.</p>
              )}
            </div>

            {/* Suggestions */}
            <div className="card">
              <h2><Lightbulb size={20} color="var(--severity-medium)" /> Suggestions</h2>
              {currentReview.suggestions.length > 0 ? (
                <div className="item-list">
                  {currentReview.suggestions.map((suggestion, i) => (
                    <div key={i} className="list-item">
                      <div className="item-header">
                        <span className="item-description">{suggestion.description}</span>
                        {suggestion.line_reference && (
                          <span className="line-ref">{suggestion.line_reference}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--text-secondary)' }}>No further suggestions.</p>
              )}
            </div>
          </div>
        ) : (
          !isLoading && (
            <div className="empty-state">
              <img src="/favicon.svg" alt="logo" style={{ width: '56px', height: '56px', opacity: 0.85 }} />
              <h3>Ready to Review</h3>
              <p>Paste your code above and click Analyze.</p>
            </div>
          )
        )}
      </main>
    </div>
  );
}

export default App;

import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import apiClient from '../api/apiClient';
import SourceList from '../components/SourceList';
import { Send, LogOut, MessageSquare, AlertTriangle, Search, Info } from 'lucide-react';

const ChatPage = () => {
    const [query, setQuery] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { logout } = useAuth();

    const handleAsk = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const response = await apiClient.post('/rag/ask', { query });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch answer. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <header className="glass-card" style={{
                padding: '1rem 2rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                margin: '1rem',
                borderRadius: '1rem'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{
                        width: '32px',
                        height: '32px',
                        background: 'var(--primary)',
                        borderRadius: '0.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <MessageSquare size={20} color="white" />
                    </div>
                    <span style={{ fontSize: '1.25rem', fontWeight: '700' }}>AI Assistant</span>
                </div>
                <button onClick={logout} style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    color: 'var(--error)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 1rem'
                }}>
                    <LogOut size={18} />
                    Sign Out
                </button>
            </header>

            {/* Main Content */}
            <main style={{ flex: 1, padding: '0 2rem 2rem 2rem', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
                <div className="glass-card" style={{ padding: '2rem', minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
                    {!result && !loading && !error && (
                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                            <Search size={48} style={{ marginBottom: '1rem' }} />
                            <h3>How can I help you today?</h3>
                            <p>Ask anything about the provided knowledge base.</p>
                        </div>
                    )}

                    {loading && (
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <div className="spinner" style={{ width: '48px', height: '48px' }} />
                        </div>
                    )}

                    {error && (
                        <div style={{
                            padding: '1.5rem',
                            background: 'rgba(239, 68, 68, 0.1)',
                            borderRadius: '0.75rem',
                            color: 'var(--error)',
                            display: 'flex',
                            gap: '1rem',
                            alignItems: 'flex-start'
                        }}>
                            <AlertTriangle size={24} />
                            <div>
                                <h4 style={{ fontWeight: '600' }}>Request Failed</h4>
                                <p style={{ fontSize: '0.875rem' }}>{error}</p>
                            </div>
                        </div>
                    )}

                    {result && (
                        <div style={{ flex: 1 }}>
                            {result.status === 'low_context' && (
                                <div style={{
                                    padding: '1rem',
                                    background: 'rgba(59, 130, 246, 0.1)',
                                    borderRadius: '0.5rem',
                                    color: '#60a5fa',
                                    marginBottom: '1.5rem',
                                    display: 'flex',
                                    gap: '0.75rem',
                                    alignItems: 'center',
                                    fontSize: '0.875rem',
                                    border: '1px solid rgba(59, 130, 246, 0.2)'
                                }}>
                                    <Info size={18} />
                                    Note: Providing an answer based on limited context.
                                </div>
                            )}

                            <div style={{ marginBottom: '2rem' }}>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '1rem' }}>Answer</h2>
                                <div style={{ fontSize: '1.125rem', color: 'rgba(255, 255, 255, 0.9)', whiteSpace: 'pre-wrap' }}>
                                    {result.answer}
                                </div>
                            </div>

                            <SourceList sources={result.sources} />
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <form onSubmit={handleAsk} style={{ marginTop: '1.5rem', position: 'relative' }}>
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Type your question here..."
                        style={{
                            padding: '1.25rem 4rem 1.25rem 1.5rem',
                            fontSize: '1rem',
                            height: 'auto',
                            borderRadius: '1rem'
                        }}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !query.trim()}
                        style={{
                            position: 'absolute',
                            right: '0.75rem',
                            top: '50%',
                            transform: 'translateY(-50%)',
                            padding: '0.625rem',
                            borderRadius: '0.75rem'
                        }}
                    >
                        <Send size={20} />
                    </button>
                </form>
            </main>
        </div>
    );
};

export default ChatPage;

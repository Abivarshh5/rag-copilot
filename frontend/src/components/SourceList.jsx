import React from 'react';
import { FileText, ExternalLink } from 'lucide-react';

const SourceList = ({ sources }) => {
    if (!sources || sources.length === 0) return null;

    return (
        <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={18} />
                Sources
            </h3>
            <div style={{ display: 'grid', gap: '0.75rem', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
                {sources.map((source, idx) => (
                    <div key={idx} className="glass-card" style={{ padding: '1rem', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                            <span style={{
                                background: 'var(--primary)',
                                color: 'white',
                                padding: '0.125rem 0.5rem',
                                borderRadius: '9999px',
                                fontSize: '0.75rem',
                                fontWeight: '600'
                            }}>
                                Score: {source.score.toFixed(4)}
                            </span>
                            {source.metadata?.url && (
                                <a href={source.metadata.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-muted)' }}>
                                    <ExternalLink size={14} />
                                </a>
                            )}
                        </div>
                        <div style={{ fontWeight: '500', color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                            {source.metadata?.title || source.id || 'Unknown Source'}
                        </div>
                        <div style={{ color: 'var(--text-muted)', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                            {source.text}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SourceList;

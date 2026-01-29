import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/apiClient';
import { UserPlus, Mail, Lock, AlertCircle, CheckCircle } from 'lucide-react';

const SignupPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (password !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        setLoading(true);

        try {
            await apiClient.post('/auth/signup', {
                email: email.trim(),
                password
            });
            setSuccess('Account created successfully! Redirecting to login...');
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create account');
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(45deg, #0f172a 0%, #1e293b 100%)',
            padding: '1rem'
        }}>
            <div className="glass-card" style={{
                width: '100%',
                maxWidth: '400px',
                padding: '2.5rem',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
            }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{
                        width: '64px',
                        height: '64px',
                        background: 'var(--primary)',
                        borderRadius: '1rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginBottom: '1rem'
                    }}>
                        <UserPlus size={32} color="white" />
                    </div>
                    <h1 style={{ fontSize: '1.875rem', fontWeight: '800', letterSpacing: '-0.025em' }}>Create Account</h1>
                    <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>Join to access the AI Copilot</p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '1.25rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>Email Address</label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="email"
                                required
                                placeholder="you@example.com"
                                style={{ paddingLeft: '2.75rem' }}
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                    </div>

                    <div style={{ marginBottom: '1.25rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>Password</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="password"
                                required
                                placeholder="••••••••"
                                style={{ paddingLeft: '2.75rem' }}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>Confirm Password</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="password"
                                required
                                placeholder="••••••••"
                                style={{ paddingLeft: '2.75rem' }}
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    {error && (
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem',
                            background: 'rgba(239, 68, 68, 0.1)',
                            borderRadius: '0.5rem',
                            color: 'var(--error)',
                            fontSize: '0.875rem',
                            marginBottom: '1.5rem',
                            border: '1px solid rgba(239, 68, 68, 0.2)'
                        }}>
                            <AlertCircle size={16} />
                            {error}
                        </div>
                    )}

                    {success && (
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem',
                            background: 'rgba(34, 197, 94, 0.1)',
                            borderRadius: '0.5rem',
                            color: '#4ade80',
                            fontSize: '0.875rem',
                            marginBottom: '1.5rem',
                            border: '1px solid rgba(34, 197, 94, 0.2)'
                        }}>
                            <CheckCircle size={16} />
                            {success}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                    >
                        {loading ? <div className="spinner" /> : 'Sign Up'}
                    </button>
                    
                    <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                        Already have an account?{' '}
                        <Link to="/login" style={{ color: 'var(--primary)', fontWeight: '600' }}>
                            Sign in
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default SignupPage;

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ErrorMessage } from '../components/ErrorMessage';
import {
  KeyRound,
  Mail,
  ArrowRight,
  CheckCircle2,
  Clock,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError({
        message: err.message || 'Login failed. Please verify credentials.',
        code: err.code || 'LOGIN_FAILED',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      {/* Left Column: SaaS Value Proposition & Features (Desktop Only) */}
      <div className="auth-hero-column">
        <div>
          {/* Brand Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px' }}>
            <div className="brand-icon" style={{ width: '42px', height: '42px', fontSize: '1.25rem' }}>
              T
            </div>
            <div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#fff' }}>
                TrackIT
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--slate-400)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Smart IT Service Platform
              </div>
            </div>
          </div>

          <h2 style={{ fontSize: '2.1rem', fontWeight: 800, lineHeight: 1.25, letterSpacing: '-0.03em', marginBottom: '20px', color: '#ffffff' }}>
            Enterprise IT service delivery, structured triage & automated SLA workflows.
          </h2>

          <p style={{ fontSize: '1rem', color: 'var(--slate-300)', lineHeight: 1.6, maxWidth: '520px', marginBottom: '36px' }}>
            Transform informal requests into accountable, auditable support tickets with rule-based priority advisory and role-based lifecycle management.
          </p>

          {/* Key Value Highlights */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
              <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(37, 99, 235, 0.2)', color: '#60a5fa' }}>
                <Sparkles size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#f8fafc' }}>
                  Smart Blast-Radius Priority Advisor
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--slate-400)', marginTop: '2px' }}>
                  Calculates objective SLA requirements based on affected systems and outage scope.
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
              <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399' }}>
                <Clock size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#f8fafc' }}>
                  Real-Time SLA Engine & Turnaround Tracking
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--slate-400)', marginTop: '2px' }}>
                  Automated breach calculation with proactive risk escalation and resolution metrics.
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
              <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(124, 58, 237, 0.2)', color: '#c084fc' }}>
                <ShieldCheck size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#f8fafc' }}>
                  Role-Based Security & Immutable Audit Logs
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--slate-400)', marginTop: '2px' }}>
                  Strict employee/agent/admin segregation with cryptographic JWT session validation.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Metric Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 18px',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          marginTop: '40px',
        }}>
          <CheckCircle2 size={20} color="#10b981" />
          <div style={{ fontSize: '0.82rem', color: 'var(--slate-300)' }}>
            <strong>Production Ready:</strong> Full-stack architecture with FastAPI, PostgreSQL, and React.
          </div>
        </div>
      </div>

      {/* Right Column: Clean White Authentication Card */}
      <div className="auth-card-column">
        <div className="auth-card">
          <div style={{ textAlign: 'center', marginBottom: '28px' }}>
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--primary-gradient)',
                color: '#fff',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: '1.3rem',
                marginBottom: '14px',
                boxShadow: '0 4px 10px rgba(37, 99, 235, 0.35)',
              }}
            >
              T
            </div>
            <h1 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--slate-900)', letterSpacing: '-0.02em' }}>
              Sign In to TrackIT
            </h1>
            <p style={{ fontSize: '0.86rem', color: 'var(--slate-500)', marginTop: '4px' }}>
              Access your corporate service management workspace
            </p>
          </div>

          {error && (
            <ErrorMessage
              message={error.message}
              code={error.code}
              onDismiss={() => setError(null)}
            />
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Corporate Email</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="email"
                  required
                  className="form-input"
                  placeholder="name@trackit.internal"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{ paddingLeft: '40px' }}
                  autoComplete="email"
                />
                <Mail
                  size={17}
                  color="var(--slate-400)"
                  style={{ position: 'absolute', left: '13px', top: '12px' }}
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '24px' }}>
              <label className="form-label">Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="password"
                  required
                  className="form-input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ paddingLeft: '40px' }}
                  autoComplete="current-password"
                />
                <KeyRound
                  size={17}
                  color="var(--slate-400)"
                  style={{ position: 'absolute', left: '13px', top: '12px' }}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', padding: '11px', fontSize: '0.92rem' }}
              disabled={loading}
            >
              {loading ? 'Authenticating...' : 'Sign In to Workspace'} <ArrowRight size={16} />
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '24px', paddingTop: '20px', borderTop: '1px solid var(--border-color)', fontSize: '0.85rem', color: 'var(--slate-500)' }}>
            New organization member?{' '}
            <Link to="/register" style={{ color: 'var(--primary)', fontWeight: 600 }}>
              Create Employee Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

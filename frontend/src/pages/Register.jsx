import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ErrorMessage } from '../components/ErrorMessage';
import {
  User,
  Mail,
  KeyRound,
  CheckCircle,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  Headphones,
} from 'lucide-react';

export const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError({ message: 'Passwords do not match', code: 'PASSWORD_MISMATCH' });
      return;
    }

    setLoading(true);
    try {
      await register({
        name,
        email,
        password,
        role: 'EMPLOYEE',
      });
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err) {
      setError({
        message: err.message || 'Registration failed',
        code: err.code || 'REGISTRATION_ERROR',
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
            Join your organization's centralized IT Service Desk.
          </h2>

          <p style={{ fontSize: '1rem', color: 'var(--slate-300)', lineHeight: 1.6, maxWidth: '520px', marginBottom: '36px' }}>
            Get direct assistance for laptop hardware, network connectivity, software licenses, VPN configuration, and IT equipment requests.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
              <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(37, 99, 235, 0.2)', color: '#60a5fa' }}>
                <Headphones size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#f8fafc' }}>
                  Dedicated Support Agent Assignment
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--slate-400)', marginTop: '2px' }}>
                  Every ticket is triaged and assigned to a qualified IT engineer within guaranteed SLA timelines.
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
              <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399' }}>
                <Sparkles size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#f8fafc' }}>
                  Transparent Lifecycle Tracking
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--slate-400)', marginTop: '2px' }}>
                  Real-time timeline steps, engineer comments, and resolution verification.
                </div>
              </div>
            </div>
          </div>
        </div>

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
          <ShieldCheck size={20} color="#10b981" />
          <div style={{ fontSize: '0.82rem', color: 'var(--slate-300)' }}>
            <strong>Enterprise Security:</strong> Passwords hashed with Bcrypt. JWT-secured API authorization.
          </div>
        </div>
      </div>

      {/* Right Column: Clean White Registration Card */}
      <div className="auth-card-column">
        <div className="auth-card">
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <h1 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--slate-900)', letterSpacing: '-0.02em' }}>
              Employee Self-Registration
            </h1>
            <p style={{ fontSize: '0.86rem', color: 'var(--slate-500)', marginTop: '4px' }}>
              Create an account with your corporate email address
            </p>
          </div>

          {error && (
            <ErrorMessage
              message={error.message}
              code={error.code}
              onDismiss={() => setError(null)}
            />
          )}

          {success && (
            <div
              style={{
                backgroundColor: 'var(--success-light)',
                border: '1px solid var(--success-border)',
                padding: '14px',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--success-text)',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.88rem',
                fontWeight: 500,
              }}
            >
              <CheckCircle size={18} color="var(--success)" />
              Account created successfully! Redirecting to login...
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  required
                  className="form-input"
                  placeholder="Sarah Connor"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  style={{ paddingLeft: '40px' }}
                />
                <User
                  size={17}
                  color="var(--slate-400)"
                  style={{ position: 'absolute', left: '13px', top: '12px' }}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Corporate Email</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="email"
                  required
                  className="form-input"
                  placeholder="s.connor@trackit.internal"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{ paddingLeft: '40px' }}
                />
                <Mail
                  size={17}
                  color="var(--slate-400)"
                  style={{ position: 'absolute', left: '13px', top: '12px' }}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Password (min 6 characters)</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="password"
                  required
                  minLength={6}
                  className="form-input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ paddingLeft: '40px' }}
                />
                <KeyRound
                  size={17}
                  color="var(--slate-400)"
                  style={{ position: 'absolute', left: '13px', top: '12px' }}
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '24px' }}>
              <label className="form-label">Confirm Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="password"
                  required
                  minLength={6}
                  className="form-input"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  style={{ paddingLeft: '40px' }}
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
              {loading ? 'Creating Account...' : 'Register Employee Account'} <ArrowRight size={16} />
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.85rem', color: 'var(--slate-500)' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600 }}>
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

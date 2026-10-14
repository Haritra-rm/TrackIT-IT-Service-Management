import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { userService } from '../services/userService';
import { ErrorMessage } from '../components/ErrorMessage';
import { User, Mail, Shield, CheckCircle2, Save } from 'lucide-react';

export const Profile = () => {
  const { user, refreshUser } = useAuth();

  const [name, setName] = useState(user?.name || '');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await userService.updateUser(user.id, { name });
      await refreshUser();
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-body" style={{ maxWidth: '640px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
          Account & Profile Settings
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
          Manage your personal details and organization role identity.
        </p>
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {success && (
        <div
          style={{
            backgroundColor: '#ecfdf5',
            border: '1px solid #a7f3d0',
            padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            color: '#065f46',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '0.9rem',
          }}
        >
          <CheckCircle2 size={18} />
          Profile updated successfully!
        </div>
      )}

      <div className="card">
        <form onSubmit={handleUpdate}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                required
                className="form-input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{ paddingLeft: '36px' }}
              />
              <User size={16} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Corporate Email Address</label>
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                disabled
                className="form-input"
                value={user?.email || ''}
                style={{ paddingLeft: '36px', backgroundColor: '#f8fafc', color: '#64748b' }}
              />
              <Mail size={16} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Primary email identity cannot be self-modified. Contact an Administrator for address updates.
            </span>
          </div>

          <div className="form-group">
            <label className="form-label">Assigned Organization Role</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                className="badge"
                style={{
                  padding: '6px 12px',
                  fontSize: '0.82rem',
                  backgroundColor: user?.role === 'ADMIN' ? 'var(--purple-light)' : user?.role === 'SUPPORT_AGENT' ? 'var(--primary-light)' : 'var(--slate-100)',
                  color: user?.role === 'ADMIN' ? 'var(--purple-text)' : user?.role === 'SUPPORT_AGENT' ? '#1e40af' : 'var(--slate-700)',
                  border: user?.role === 'ADMIN' ? '1px solid var(--purple-border)' : user?.role === 'SUPPORT_AGENT' ? '1px solid var(--primary-border)' : '1px solid var(--slate-300)',
                }}
              >
                <Shield size={13} strokeWidth={2.5} /> {user?.role}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              <Save size={16} /> {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

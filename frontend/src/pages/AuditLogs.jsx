import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/dashboardService';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { FileText, Shield, User, Clock, Filter } from 'lucide-react';

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [entityFilter, setEntityFilter] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardService.getAuditLogs(100, entityFilter || null);
      setLogs(data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch audit logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [entityFilter]);

  const getActionColor = (action) => {
    if (action.includes('CREATED') || action.includes('REGISTERED')) return '#059669';
    if (action.includes('DELETED')) return '#dc2626';
    if (action.includes('STATUS') || action.includes('ASSIGNED')) return '#2563eb';
    return '#64748b';
  };

  return (
    <div className="page-body">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
            System Security & Audit Trail
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
            Immutable chronological logging of all critical actions, mutations, and user activities.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={16} color="#64748b" />
          <select
            className="form-select"
            value={entityFilter}
            onChange={(e) => setEntityFilter(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="">All Entity Types</option>
            <option value="TICKET">Tickets Only</option>
            <option value="USER">Users Only</option>
            <option value="CATEGORY">Categories Only</option>
          </select>
        </div>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchLogs} />}

      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <LoadingSpinner message="Fetching system audit log records..." />
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>Log ID</th>
                  <th>Action</th>
                  <th>Target Entity</th>
                  <th>Triggered By</th>
                  <th>Details / Metadata</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '36px', color: '#64748b' }}>
                      No audit events found.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id}>
                      <td style={{ fontFamily: 'JetBrains Mono', color: '#64748b' }}>#{log.id}</td>
                      <td>
                        <span
                          style={{
                            fontFamily: 'JetBrains Mono',
                            fontSize: '0.8rem',
                            fontWeight: 700,
                            color: getActionColor(log.action),
                          }}
                        >
                          {log.action}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontWeight: 600 }}>
                          {log.entity_type} {log.entity_id ? `(#${log.entity_id})` : ''}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <User size={14} color="#64748b" />
                          <span>{log.user_name || 'System / Anonymous'}</span>
                        </div>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: '#64748b', maxWidth: '300px' }}>
                        {log.metadata_json ? (
                          <code style={{ fontSize: '0.75rem', backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>
                            {log.metadata_json}
                          </code>
                        ) : (
                          '—'
                        )}
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

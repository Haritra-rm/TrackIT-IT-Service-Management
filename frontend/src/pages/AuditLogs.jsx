import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/dashboardService';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { Modal } from '../components/Modal';
import { FileText, Shield, User, Clock, Filter, Eye, Copy, Check } from 'lucide-react';

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [entityFilter, setEntityFilter] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);
  const [copied, setCopied] = useState(false);

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

  const getPrettyJson = (raw) => {
    if (!raw) return '{\n  /* No additional metadata */\n}';
    if (typeof raw === 'object') {
      return JSON.stringify(raw, null, 2);
    }
    try {
      const parsed = JSON.parse(raw);
      return JSON.stringify(parsed, null, 2);
    } catch (e) {
      return String(raw);
    }
  };

  const handleCopyJson = () => {
    if (!selectedLog) return;
    const text = getPrettyJson(selectedLog.metadata_json);
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }).catch(() => {});
    }
  };

  return (
    <div className="page-body">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
            System Security & Audit Trail
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
            Append-only chronological logging of critical actions, mutations, and user activities.
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
          <div className="table-container" style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
            <table className="data-table" style={{ minWidth: '950px' }}>
              <thead>
                <tr>
                  <th style={{ width: '80px', minWidth: '80px' }}>Log ID</th>
                  <th style={{ width: '190px', minWidth: '180px' }}>Action</th>
                  <th style={{ width: '150px', minWidth: '140px' }}>Target Entity</th>
                  <th style={{ width: '160px', minWidth: '150px' }}>Triggered By</th>
                  <th style={{ width: '280px', minWidth: '240px', maxWidth: '300px' }}>Details / Metadata</th>
                  <th style={{ width: '180px', minWidth: '180px', whiteSpace: 'nowrap' }}>Timestamp</th>
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
                  logs.map((log) => {
                    const hasMetadata = Boolean(
                      log.metadata_json &&
                      log.metadata_json !== '{}' &&
                      log.metadata_json !== 'null'
                    );
                    const rawString = typeof log.metadata_json === 'string'
                      ? log.metadata_json
                      : JSON.stringify(log.metadata_json);

                    return (
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
                        <td style={{ width: '280px', maxWidth: '300px' }}>
                          {hasMetadata ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', maxWidth: '100%' }}>
                              <span
                                title={`${rawString} (Click to inspect complete payload)`}
                                onClick={() => setSelectedLog(log)}
                                style={{
                                  fontFamily: 'JetBrains Mono, monospace',
                                  fontSize: '0.75rem',
                                  backgroundColor: '#f1f5f9',
                                  color: '#475569',
                                  padding: '3px 8px',
                                  borderRadius: '4px',
                                  border: '1px solid #e2e8f0',
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap',
                                  maxWidth: '180px',
                                  cursor: 'pointer',
                                  display: 'inline-block',
                                  userSelect: 'none'
                                }}
                              >
                                {rawString}
                              </span>
                              <button
                                type="button"
                                onClick={() => setSelectedLog(log)}
                                className="btn-secondary"
                                style={{
                                  padding: '3px 8px',
                                  fontSize: '0.72rem',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  whiteSpace: 'nowrap',
                                  cursor: 'pointer',
                                  flexShrink: 0,
                                  height: '24px'
                                }}
                                title="View full metadata"
                                aria-label={`View full metadata for log #${log.id}`}
                              >
                                <Eye size={12} />
                                <span>View</span>
                              </button>
                            </div>
                          ) : (
                            <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.85rem' }}>—</span>
                          )}
                        </td>
                        <td style={{ width: '180px', minWidth: '180px', fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <Clock size={13} color="#94a3b8" />
                            <span>{new Date(log.timestamp).toLocaleString()}</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedLog && (
        <Modal
          isOpen={Boolean(selectedLog)}
          onClose={() => {
            setSelectedLog(null);
            setCopied(false);
          }}
          title={`Audit Event Details #${selectedLog.id}`}
          maxWidth="640px"
          footer={
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', width: '100%' }}>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => {
                  setSelectedLog(null);
                  setCopied(false);
                }}
              >
                Close
              </button>
            </div>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '12px',
                background: 'var(--slate-50, #f8fafc)',
                padding: '12px 16px',
                borderRadius: '8px',
                border: '1px solid var(--border-color, #e2e8f0)',
                fontSize: '0.82rem'
              }}
            >
              <div>
                <div style={{ color: 'var(--text-muted, #64748b)', fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase' }}>
                  Action
                </div>
                <div style={{ fontWeight: 700, fontFamily: 'JetBrains Mono', color: getActionColor(selectedLog.action), marginTop: '2px' }}>
                  {selectedLog.action}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted, #64748b)', fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase' }}>
                  Target Entity
                </div>
                <div style={{ fontWeight: 600, marginTop: '2px' }}>
                  {selectedLog.entity_type} {selectedLog.entity_id ? `(#${selectedLog.entity_id})` : ''}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted, #64748b)', fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase' }}>
                  Triggered By
                </div>
                <div style={{ fontWeight: 600, marginTop: '2px' }}>
                  {selectedLog.user_name || 'System / Anonymous'}
                </div>
              </div>
              <div>
                <div style={{ color: 'var(--text-muted, #64748b)', fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase' }}>
                  Timestamp
                </div>
                <div style={{ color: 'var(--text-muted, #64748b)', marginTop: '2px' }}>
                  {new Date(selectedLog.timestamp).toLocaleString()}
                </div>
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-main, #1e293b)' }}>
                  Event Metadata Payload
                </span>
                <button
                  type="button"
                  onClick={handleCopyJson}
                  className="btn-secondary"
                  style={{
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    borderRadius: '6px'
                  }}
                >
                  {copied ? (
                    <>
                      <Check size={13} color="#059669" />
                      <span style={{ color: '#059669', fontWeight: 600 }}>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy size={13} />
                      <span>Copy JSON</span>
                    </>
                  )}
                </button>
              </div>

              <pre
                style={{
                  margin: 0,
                  background: '#0f172a',
                  color: '#38bdf8',
                  padding: '16px',
                  borderRadius: '8px',
                  overflowX: 'auto',
                  fontSize: '0.82rem',
                  fontFamily: 'JetBrains Mono, monospace',
                  lineHeight: '1.5',
                  maxHeight: '340px',
                  border: '1px solid #1e293b'
                }}
              >
                <code>{getPrettyJson(selectedLog.metadata_json)}</code>
              </pre>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

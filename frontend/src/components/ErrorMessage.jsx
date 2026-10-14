import React from 'react';
import { AlertCircle, RefreshCw, X } from 'lucide-react';

export const ErrorMessage = ({ message, code, onRetry, onDismiss }) => {
  if (!message) return null;

  return (
    <div
      style={{
        backgroundColor: '#fef2f2',
        border: '1px solid #fecaca',
        borderRadius: 'var(--radius-sm)',
        padding: '14px 18px',
        color: '#991b1b',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        margin: '16px 0',
      }}
    >
      <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>
          {code ? `Error (${code})` : 'Operation Error'}
        </div>
        <div style={{ fontSize: '0.85rem', marginTop: '2px', color: '#b91c1c' }}>
          {message}
        </div>
      </div>
      <div style={{ display: 'flex', gap: '8px' }}>
        {onRetry && (
          <button
            onClick={onRetry}
            className="btn btn-sm btn-secondary"
            style={{ borderColor: '#fca5a5', color: '#991b1b' }}
          >
            <RefreshCw size={14} /> Retry
          </button>
        )}
        {onDismiss && (
          <button onClick={onDismiss} style={{ color: '#991b1b', padding: '4px' }}>
            <X size={16} />
          </button>
        )}
      </div>
    </div>
  );
};

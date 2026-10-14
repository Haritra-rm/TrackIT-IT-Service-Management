import React from 'react';
import { Modal } from './Modal';
import { AlertTriangle } from 'lucide-react';

export const ConfirmDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDestructive = false,
  loading = false,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      maxWidth="460px"
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
            {cancelText}
          </button>
          <button
            className={`btn ${isDestructive ? 'btn-danger' : 'btn-primary'}`}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? 'Processing...' : confirmText}
          </button>
        </>
      }
    >
      <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
        {isDestructive && (
          <div
            style={{
              padding: '10px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: '#fee2e2',
              color: '#dc2626',
            }}
          >
            <AlertTriangle size={24} />
          </div>
        )}
        <div style={{ fontSize: '0.95rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
          {message}
        </div>
      </div>
    </Modal>
  );
};

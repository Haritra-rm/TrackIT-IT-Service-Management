import React, { useState } from 'react';
import { Modal } from './Modal';
import { PriorityBadge } from './PriorityBadge';
import { ticketService } from '../services/ticketService';
import { Sparkles, Check, CheckCircle2, Clock, ShieldAlert, AlertTriangle } from 'lucide-react';

export const PriorityRecommenderModal = ({ isOpen, onClose, onSelectPriority, defaultCategory = '' }) => {
  const [affectedUsers, setAffectedUsers] = useState(1);
  const [businessImpact, setBusinessImpact] = useState('LOW');
  const [isSecurityIncident, setIsSecurityIncident] = useState(false);
  const [isSystemDown, setIsSystemDown] = useState(false);

  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const res = await ticketService.recommendPriority({
        category_name: defaultCategory,
        affected_users: Number(affectedUsers),
        business_impact: businessImpact,
        is_security_incident: isSecurityIncident,
        is_system_down: isSystemDown,
      });
      setRecommendation(res);
    } catch (err) {
      console.error('Error calculating recommendation:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    if (recommendation) {
      onSelectPriority(recommendation.recommended_priority);
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Smart Priority Advisor (Rule-Based Engine)"
      maxWidth="560px"
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          {recommendation && (
            <button className="btn btn-primary" onClick={handleApply}>
              <Check size={16} /> Apply {recommendation.recommended_priority}
            </button>
          )}
        </>
      }
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
        <div style={{
          backgroundColor: 'var(--primary-light)',
          border: '1px solid var(--primary-border)',
          borderRadius: 'var(--radius-sm)',
          padding: '12px 16px',
          fontSize: '0.85rem',
          color: '#1e40af',
          display: 'flex',
          gap: '10px',
          alignItems: 'flex-start',
        }}>
          <Sparkles size={18} color="#2563eb" style={{ flexShrink: 0, marginTop: '2px' }} />
          <span>
            TrackIT's Smart Recommendation Engine evaluates blast radius, infrastructure criticality, and security impact to recommend the objective priority level according to organization SLA guidelines.
          </span>
        </div>

        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">How many users or systems are impacted?</label>
          <input
            type="number"
            min="1"
            className="form-input"
            value={affectedUsers}
            onChange={(e) => setAffectedUsers(e.target.value)}
          />
          <span className="form-helper">
            1 = Individual, 2-19 = Department/Team, 20+ = Enterprise-wide Outage
          </span>
        </div>

        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label">Business Operational Impact</label>
          <select
            className="form-select"
            value={businessImpact}
            onChange={(e) => setBusinessImpact(e.target.value)}
          >
            <option value="LOW">Low (Work continues normally, minor inconvenience)</option>
            <option value="MEDIUM">Medium (Productivity impaired, standard workaround exists)</option>
            <option value="HIGH">High (Key business workflow or deliverables blocked)</option>
            <option value="CRITICAL">Critical (Company-wide work halt / financial or legal risk)</option>
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              border: isSecurityIncident ? '1px solid #fca5a5' : '1px solid var(--border-color)',
              backgroundColor: isSecurityIncident ? '#fef2f2' : '#ffffff',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
            }}
          >
            <input
              type="checkbox"
              checked={isSecurityIncident}
              onChange={(e) => setIsSecurityIncident(e.target.checked)}
              style={{ width: '16px', height: '16px' }}
            />
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.88rem' }}>
              <ShieldAlert size={16} color={isSecurityIncident ? '#dc2626' : '#64748b'} />
              <span style={{ fontWeight: 500, color: isSecurityIncident ? '#991b1b' : 'var(--text-main)' }}>
                Active Security Incident / Data Leak Risk
              </span>
            </div>
          </label>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              border: isSystemDown ? '1px solid #fed7aa' : '1px solid var(--border-color)',
              backgroundColor: isSystemDown ? '#fff7ed' : '#ffffff',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
            }}
          >
            <input
              type="checkbox"
              checked={isSystemDown}
              onChange={(e) => setIsSystemDown(e.target.checked)}
              style={{ width: '16px', height: '16px' }}
            />
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.88rem' }}>
              <AlertTriangle size={16} color={isSystemDown ? '#ea580c' : '#64748b'} />
              <span style={{ fontWeight: 500, color: isSystemDown ? '#9a3412' : 'var(--text-main)' }}>
                Core production system or service is completely down
              </span>
            </div>
          </label>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={handleCalculate}
          disabled={loading}
          style={{ alignSelf: 'flex-start' }}
        >
          <Sparkles size={16} color="#2563eb" /> {loading ? 'Evaluating SLA Rules...' : 'Compute Recommendation'}
        </button>

        {/* Polished Recommendation Card */}
        {recommendation && (
          <div
            style={{
              marginTop: '6px',
              padding: '18px 20px',
              backgroundColor: '#f8fafc',
              border: '1px solid #cbd5e1',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-xs)',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Recommended Priority Level
              </span>
              <PriorityBadge priority={recommendation.recommended_priority} />
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
              <CheckCircle2 size={16} color="#10b981" style={{ flexShrink: 0, marginTop: '3px' }} />
              <div style={{ fontSize: '0.88rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                <strong>Decision Rationale:</strong> {recommendation.reasoning}
              </div>
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              backgroundColor: '#eff6ff',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.82rem',
              color: '#1d4ed8',
              fontWeight: 600,
            }}>
              <Clock size={15} />
              <span>Target SLA Resolution Window: Within {recommendation.sla_hours} hours</span>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};

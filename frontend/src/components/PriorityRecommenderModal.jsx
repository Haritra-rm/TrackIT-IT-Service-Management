import React, { useState } from 'react';
import { Modal } from './Modal';
import { PriorityBadge } from './PriorityBadge';
import { ticketService } from '../services/ticketService';
import { Sparkles, Check, HelpCircle } from 'lucide-react';

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
      maxWidth="540px"
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
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
          TrackIT's Smart Recommendation Engine evaluates blast radius, infrastructure criticality, and security impact to recommend the objective priority level according to organization SLA guidelines.
        </p>

        <div className="form-group">
          <label className="form-label">How many users are impacted?</label>
          <input
            type="number"
            min="1"
            className="form-input"
            value={affectedUsers}
            onChange={(e) => setAffectedUsers(e.target.value)}
          />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            1 = Individual, 2-19 = Department/Team, 20+ = Enterprise-wide
          </span>
        </div>

        <div className="form-group">
          <label className="form-label">Business Operational Impact</label>
          <select
            className="form-select"
            value={businessImpact}
            onChange={(e) => setBusinessImpact(e.target.value)}
          >
            <option value="LOW">Low (Work continues normally, minor inconvenience)</option>
            <option value="MEDIUM">Medium (Productivity impaired, workaround exists)</option>
            <option value="HIGH">High (Key business process or deliverables blocked)</option>
            <option value="CRITICAL">Critical (Company-wide work halt / financial loss)</option>
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.88rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={isSecurityIncident}
              onChange={(e) => setIsSecurityIncident(e.target.checked)}
            />
            <span>This is an active Security Incident / Data Exposure alert</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.88rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={isSystemDown}
              onChange={(e) => setIsSystemDown(e.target.checked)}
            />
            <span>Core production system or service is completely down</span>
          </label>
        </div>

        <button
          className="btn btn-secondary"
          onClick={handleCalculate}
          disabled={loading}
          style={{ alignSelf: 'flex-start', marginTop: '6px' }}
        >
          <Sparkles size={16} color="#3b82f6" /> {loading ? 'Evaluating...' : 'Compute Recommendation'}
        </button>

        {recommendation && (
          <div
            style={{
              marginTop: '12px',
              padding: '16px',
              backgroundColor: '#f8fafc',
              border: '1px solid #cbd5e1',
              borderRadius: 'var(--radius-sm)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                RECOMMENDED PRIORITY:
              </span>
              <PriorityBadge priority={recommendation.recommended_priority} />
            </div>

            <div style={{ fontSize: '0.88rem', color: 'var(--text-main)', marginBottom: '8px' }}>
              <strong>Reasoning:</strong> {recommendation.reasoning}
            </div>

            <div style={{ fontSize: '0.8rem', color: '#475569' }}>
              <strong>Target SLA Resolution:</strong> Within {recommendation.sla_hours} hours.
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};

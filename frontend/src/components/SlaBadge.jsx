import React from 'react';
import { ShieldCheck, AlertTriangle, Flame, Check } from 'lucide-react';

export const SlaBadge = ({ slaStatus, remainingHours, isBreached }) => {
  let config = {
    label: 'On Track',
    className: 'badge-sla-ON_TRACK',
    icon: ShieldCheck,
  };

  if (slaStatus === 'MET') {
    config = { label: 'SLA Met', className: 'badge-sla-MET', icon: Check };
  } else if (isBreached || slaStatus === 'BREACHED') {
    config = { label: 'SLA Breached', className: 'badge-sla-BREACHED', icon: Flame };
  } else if (slaStatus === 'AT_RISK') {
    config = { label: 'SLA At Risk', className: 'badge-sla-AT_RISK', icon: AlertTriangle };
  }

  const Icon = config.icon;

  let timeText = '';
  if (remainingHours !== null && remainingHours !== undefined && slaStatus !== 'MET') {
    if (remainingHours < 0) {
      timeText = ` (${Math.abs(remainingHours)}h overdue)`;
    } else {
      timeText = ` (${remainingHours}h left)`;
    }
  }

  return (
    <span className={`badge ${config.className}`} title={`SLA status: ${config.label}`}>
      <Icon size={12} strokeWidth={2.5} />
      {config.label}
      {timeText && <span style={{ opacity: 0.9, fontWeight: 500 }}>{timeText}</span>}
    </span>
  );
};

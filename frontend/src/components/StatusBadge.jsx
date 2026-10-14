import React from 'react';
import { CircleDot, CheckCircle2, Clock, RotateCcw, XCircle, Play } from 'lucide-react';

const STATUS_CONFIG = {
  OPEN: { label: 'Open', className: 'badge-status-OPEN', icon: CircleDot },
  ASSIGNED: { label: 'Assigned', className: 'badge-status-ASSIGNED', icon: Clock },
  IN_PROGRESS: { label: 'In Progress', className: 'badge-status-IN_PROGRESS', icon: Play },
  RESOLVED: { label: 'Resolved', className: 'badge-status-RESOLVED', icon: CheckCircle2 },
  CLOSED: { label: 'Closed', className: 'badge-status-CLOSED', icon: XCircle },
  REOPENED: { label: 'Reopened', className: 'badge-status-REOPENED', icon: RotateCcw },
};

export const StatusBadge = ({ status }) => {
  const config = STATUS_CONFIG[status] || {
    label: status || 'Unknown',
    className: 'badge-status-OPEN',
    icon: CircleDot,
  };
  const Icon = config.icon;

  return (
    <span className={`badge ${config.className}`}>
      <Icon size={11} strokeWidth={2.5} />
      <span>{config.label}</span>
    </span>
  );
};

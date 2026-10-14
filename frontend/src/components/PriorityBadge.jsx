import React from 'react';
import { ArrowDown, Minus, ArrowUp, AlertOctagon } from 'lucide-react';

const PRIORITY_CONFIG = {
  LOW: { label: 'Low', className: 'badge-priority-LOW', icon: ArrowDown },
  MEDIUM: { label: 'Medium', className: 'badge-priority-MEDIUM', icon: Minus },
  HIGH: { label: 'High', className: 'badge-priority-HIGH', icon: ArrowUp },
  CRITICAL: { label: 'Critical', className: 'badge-priority-CRITICAL', icon: AlertOctagon },
};

export const PriorityBadge = ({ priority }) => {
  const config = PRIORITY_CONFIG[priority] || {
    label: priority || 'Medium',
    className: 'badge-priority-MEDIUM',
    icon: Minus,
  };
  const Icon = config.icon;

  return (
    <span className={`badge ${config.className}`}>
      <Icon size={11} strokeWidth={2.5} />
      <span>{config.label}</span>
    </span>
  );
};

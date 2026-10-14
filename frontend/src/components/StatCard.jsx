import React from 'react';

const COLOR_MAP = {
  blue: { accent: '#2563eb', bg: '#eff6ff', text: '#2563eb' },
  indigo: { accent: '#4f46e5', bg: '#eef2ff', text: '#4f46e5' },
  violet: { accent: '#7c3aed', bg: '#f5f3ff', text: '#7c3aed' },
  purple: { accent: '#7c3aed', bg: '#f5f3ff', text: '#7c3aed' },
  cyan: { accent: '#0891b2', bg: '#ecfeff', text: '#0891b2' },
  green: { accent: '#10b981', bg: '#ecfdf5', text: '#059669' },
  amber: { accent: '#f59e0b', bg: '#fffbeb', text: '#d97706' },
  orange: { accent: '#ea580c', bg: '#fff7ed', text: '#ea580c' },
  red: { accent: '#ef4444', bg: '#fef2f2', text: '#dc2626' },
};

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'blue' }) => {
  const scheme = COLOR_MAP[color] || COLOR_MAP.blue;

  return (
    <div
      className="stat-card"
      style={{ '--card-accent': scheme.accent }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="stat-value">{value ?? 0}</div>
        <div className="stat-label">{title}</div>
        {subtitle && (
          <div className="stat-subtitle">{subtitle}</div>
        )}
      </div>

      {Icon && (
        <div
          className="stat-icon-wrapper"
          style={{ backgroundColor: scheme.bg, color: scheme.text }}
          aria-hidden="true"
        >
          <Icon size={22} strokeWidth={2.2} />
        </div>
      )}
    </div>
  );
};

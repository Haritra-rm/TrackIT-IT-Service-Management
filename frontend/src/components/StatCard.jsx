import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'blue' }) => {
  const colorMap = {
    blue: { bg: '#eff6ff', text: '#2563eb' },
    green: { bg: '#ecfdf5', text: '#059669' },
    amber: { bg: '#fffbeb', text: '#d97706' },
    red: { bg: '#fef2f2', text: '#dc2626' },
    purple: { bg: '#f5f3ff', text: '#7c3aed' },
    indigo: { bg: '#eef2ff', text: '#4f46e5' },
  };

  const scheme = colorMap[color] || colorMap.blue;

  return (
    <div className="stat-card">
      <div>
        <div className="stat-value">{value ?? 0}</div>
        <div className="stat-label">{title}</div>
        {subtitle && (
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            {subtitle}
          </div>
        )}
      </div>
      {Icon && (
        <div
          className="stat-icon-wrapper"
          style={{ backgroundColor: scheme.bg, color: scheme.text }}
        >
          <Icon size={24} strokeWidth={2} />
        </div>
      )}
    </div>
  );
};

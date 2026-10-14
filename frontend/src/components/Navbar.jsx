import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { PlusCircle, Bell, Shield, LifeBuoy } from 'lucide-react';

export const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  const getBreadcrumb = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/tickets/create')) return 'Tickets / Raise New Issue';
    if (path.startsWith('/tickets/')) return 'Tickets / Ticket Details';
    if (path.startsWith('/tickets')) return 'Tickets / Ticket Directory';
    if (path.startsWith('/users')) return 'Administration / User Directory';
    if (path.startsWith('/categories')) return 'Administration / Issue Categories';
    if (path.startsWith('/reports')) return 'Analytics / Performance & KPIs';
    if (path.startsWith('/audit-logs')) return 'Administration / System Audit Trail';
    if (path.startsWith('/profile')) return 'My Account / Profile';
    return 'TrackIT Portal';
  };

  return (
    <header className="top-navbar">
      <div className="navbar-breadcrumbs">
        <span style={{ color: 'var(--text-light)' }}>TrackIT</span>
        <span>/</span>
        <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{getBreadcrumb()}</span>
      </div>

      <div className="navbar-actions">
        {/* System Status Indicator */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.8rem',
            color: '#059669',
            backgroundColor: '#ecfdf5',
            padding: '4px 10px',
            borderRadius: 'var(--radius-full)',
            fontWeight: 600,
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#10b981',
              display: 'inline-block',
            }}
          />
          Live
        </div>

        {/* Quick Raise Ticket CTA */}
        <button
          className="btn btn-sm btn-primary"
          onClick={() => navigate('/tickets/create')}
        >
          <PlusCircle size={15} /> Raise Issue
        </button>
      </div>
    </header>
  );
};

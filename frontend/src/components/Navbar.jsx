import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { PlusCircle, Menu } from 'lucide-react';

export const Navbar = ({ onToggleMobile }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const getBreadcrumb = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/tickets/create')) return 'Tickets / Raise New Issue';
    if (path.startsWith('/tickets/')) return 'Tickets / Details';
    if (path.startsWith('/tickets')) return 'Tickets / Directory';
    if (path.startsWith('/users')) return 'Administration / Users';
    if (path.startsWith('/categories')) return 'Administration / Categories';
    if (path.startsWith('/reports')) return 'Analytics / Performance & KPIs';
    if (path.startsWith('/audit-logs')) return 'Administration / Audit Trail';
    if (path.startsWith('/profile')) return 'Account / Profile';
    return 'Portal';
  };

  return (
    <header className="top-navbar" aria-label="Main Navigation Header">
      <div className="navbar-left">
        {/* Mobile Hamburger Drawer Toggle Button */}
        <button
          className="navbar-hamburger"
          onClick={onToggleMobile}
          aria-label="Toggle navigation menu"
        >
          <Menu size={20} />
        </button>

        {/* Dynamic Responsive Breadcrumbs */}
        <div className="navbar-breadcrumbs">
          <span style={{ color: 'var(--text-light)', fontWeight: 500 }}>TrackIT</span>
          <span style={{ color: 'var(--slate-300)' }}>/</span>
          <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{getBreadcrumb()}</span>
        </div>
      </div>

      <div className="navbar-actions">
        {/* Live Operational Health Status */}
        <div className="live-indicator" title="IT Systems & SLA Engine: Operational">
          <span className="live-dot" />
          <span>Live Ops</span>
        </div>

        {/* Fast Action CTA */}
        <button
          className="btn btn-sm btn-primary"
          onClick={() => navigate('/tickets/create')}
        >
          <PlusCircle size={15} /> <span>Raise Issue</span>
        </button>
      </div>
    </header>
  );
};

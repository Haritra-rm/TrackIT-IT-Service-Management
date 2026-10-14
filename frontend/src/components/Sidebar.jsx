import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import {
  LayoutDashboard,
  Ticket,
  PlusCircle,
  Users,
  FolderKanban,
  BarChart3,
  FileText,
  User,
  LogOut,
  ShieldAlert,
  Headphones,
} from 'lucide-react';

export const Sidebar = () => {
  const { user, role, isEmployee, isAgent, isAdmin, logout } = useAuth();

  const getRoleLabel = () => {
    if (isAdmin) return 'Administrator';
    if (isAgent) return 'Support Agent';
    return 'Employee';
  };

  const getRoleBadgeStyle = () => {
    if (isAdmin) return { backgroundColor: '#7c3aed', color: '#fff' };
    if (isAgent) return { backgroundColor: '#2563eb', color: '#fff' };
    return { backgroundColor: '#059669', color: '#fff' };
  };

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-icon">T</div>
        <div>
          <div className="brand-title">TrackIT</div>
          <div className="brand-subtitle">IT Service Ops</div>
        </div>
      </div>

      {/* Role Pill */}
      <div style={{ padding: '12px 18px', borderBottom: '1px solid #1e293b' }}>
        <span
          style={{
            ...getRoleBadgeStyle(),
            padding: '3px 8px',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.7rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          {isAdmin && <ShieldAlert size={12} />}
          {isAgent && <Headphones size={12} />}
          {getRoleLabel()}
        </span>
      </div>

      {/* Navigation Links */}
      <nav className="sidebar-nav">
        <div className="nav-section-title">Overview</div>
        <NavLink
          to="/"
          end
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <LayoutDashboard size={18} />
          <span className="nav-text">Dashboard</span>
        </NavLink>

        <div className="nav-section-title">Ticket Management</div>
        <NavLink
          to="/tickets"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Ticket size={18} />
          <span className="nav-text">{isEmployee ? 'My Tickets' : 'All Tickets'}</span>
        </NavLink>

        <NavLink
          to="/tickets/create"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <PlusCircle size={18} />
          <span className="nav-text">Raise Ticket</span>
        </NavLink>

        {(isAgent || isAdmin) && (
          <>
            <div className="nav-section-title">Operations & Reports</div>
            <NavLink
              to="/reports"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <BarChart3 size={18} />
              <span className="nav-text">Analytics & KPIs</span>
            </NavLink>
          </>
        )}

        {isAdmin && (
          <>
            <div className="nav-section-title">Administration</div>
            <NavLink
              to="/users"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <Users size={18} />
              <span className="nav-text">User Management</span>
            </NavLink>

            <NavLink
              to="/categories"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <FolderKanban size={18} />
              <span className="nav-text">Categories</span>
            </NavLink>

            <NavLink
              to="/audit-logs"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <FileText size={18} />
              <span className="nav-text">System Audit Logs</span>
            </NavLink>
          </>
        )}

        <div className="nav-section-title" style={{ marginTop: 'auto' }}>Account</div>
        <NavLink
          to="/profile"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <User size={18} />
          <span className="nav-text">My Profile</span>
        </NavLink>
      </nav>

      {/* User Footer with Logout */}
      <div className="sidebar-user">
        <div className="user-avatar">
          {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
        </div>
        <div className="user-details" style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {user?.name || 'User'}
          </div>
          <div
            style={{
              fontSize: '0.72rem',
              color: '#94a3b8',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {user?.email || ''}
          </div>
        </div>
        <button
          onClick={logout}
          title="Logout"
          style={{
            color: '#94a3b8',
            padding: '6px',
            borderRadius: '4px',
            transition: 'color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#ef4444')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#94a3b8')}
        >
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
};

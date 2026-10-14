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
  UserCheck,
  X,
} from 'lucide-react';

export const Sidebar = ({ isOpen = false, onClose }) => {
  const { user, isEmployee, isAgent, isAdmin, logout } = useAuth();

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

  const handleNavClick = () => {
    if (onClose) onClose();
  };

  return (
    <aside className={`sidebar ${isOpen ? 'mobile-open' : ''}`} aria-label="Sidebar Navigation">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-wrapper">
          <div className="brand-icon">T</div>
          <div>
            <div className="brand-title">TrackIT</div>
            <div className="brand-subtitle">IT Service Ops</div>
          </div>
        </div>

        {/* Mobile Close Button */}
        <button
          className="sidebar-close-btn"
          onClick={onClose}
          aria-label="Close navigation menu"
        >
          <X size={20} />
        </button>
      </div>

      {/* Role Pill */}
      <div className="sidebar-role-pill">
        <span
          className="role-badge"
          style={getRoleBadgeStyle()}
        >
          {isAdmin && <ShieldAlert size={12} />}
          {isAgent && <Headphones size={12} />}
          {isEmployee && <UserCheck size={12} />}
          {getRoleLabel()}
        </span>
      </div>

      {/* Navigation Links */}
      <nav className="sidebar-nav">
        <div className="nav-section-title">Overview</div>
        <NavLink
          to="/"
          end
          onClick={handleNavClick}
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>

        <div className="nav-section-title">Ticket Management</div>
        <NavLink
          to="/tickets"
          onClick={handleNavClick}
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Ticket size={18} />
          <span>{isEmployee ? 'My Tickets' : 'All Tickets'}</span>
        </NavLink>

        <NavLink
          to="/tickets/create"
          onClick={handleNavClick}
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <PlusCircle size={18} />
          <span>Raise Ticket</span>
        </NavLink>

        {(isAgent || isAdmin) && (
          <>
            <div className="nav-section-title">Operations & Reports</div>
            <NavLink
              to="/reports"
              onClick={handleNavClick}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <BarChart3 size={18} />
              <span>Analytics & KPIs</span>
            </NavLink>
          </>
        )}

        {isAdmin && (
          <>
            <div className="nav-section-title">Administration</div>
            <NavLink
              to="/users"
              onClick={handleNavClick}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <Users size={18} />
              <span>User Management</span>
            </NavLink>

            <NavLink
              to="/categories"
              onClick={handleNavClick}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <FolderKanban size={18} />
              <span>Categories</span>
            </NavLink>

            <NavLink
              to="/audit-logs"
              onClick={handleNavClick}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <FileText size={18} />
              <span>System Audit Logs</span>
            </NavLink>
          </>
        )}

        <div className="nav-section-title" style={{ marginTop: 'auto' }}>Account</div>
        <NavLink
          to="/profile"
          onClick={handleNavClick}
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <User size={18} />
          <span>My Profile</span>
        </NavLink>
      </nav>

      {/* User Footer with Logout */}
      <div className="sidebar-user">
        <div className="user-avatar">
          {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              color: '#ffffff',
            }}
          >
            {user?.name || 'User'}
          </div>
          <div
            style={{
              fontSize: '0.72rem',
              color: 'var(--slate-400)',
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
            color: 'var(--slate-400)',
            padding: '8px',
            borderRadius: 'var(--radius-xs)',
            transition: 'color var(--transition-fast)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#ef4444')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--slate-400)')}
          aria-label="Log out of TrackIT"
        >
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
};

import React, { useState, useEffect } from 'react';
import { userService } from '../services/userService';
import { authService } from '../services/authService';
import { Modal } from '../components/Modal';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import {
  Users,
  UserPlus,
  Search,
  CheckCircle,
  XCircle,
  Shield,
  Headphones,
  User,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export const UsersManagement = () => {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);

  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [activeFilter, setActiveFilter] = useState('');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Toggle status dialog state
  const [targetUser, setTargetUser] = useState(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [toggleLoading, setToggleLoading] = useState(false);

  // Create user modal state
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'SUPPORT_AGENT',
  });
  const [createLoading, setCreateLoading] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (search.trim()) params.search = search.trim();
      if (roleFilter) params.role = roleFilter;
      if (activeFilter !== '') params.is_active = activeFilter === 'true';

      const res = await userService.listUsers(params);
      setUsers(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      setError(err.message || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page, pageSize, roleFilter, activeFilter]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchUsers();
  };

  const handleToggleStatus = async () => {
    if (!targetUser) return;
    setToggleLoading(true);
    try {
      await userService.updateStatus(targetUser.id, !targetUser.is_active);
      setIsConfirmOpen(false);
      setTargetUser(null);
      fetchUsers();
    } catch (err) {
      setError(err.message || 'Failed to update user status');
    } finally {
      setToggleLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setCreateLoading(true);
    try {
      await authService.register(createForm);
      setIsCreateOpen(false);
      setCreateForm({ name: '', email: '', password: '', role: 'SUPPORT_AGENT' });
      fetchUsers();
    } catch (err) {
      setError(err.message || 'Failed to create user');
    } finally {
      setCreateLoading(false);
    }
  };

  const getRoleBadge = (role) => {
    if (role === 'ADMIN') {
      return (
        <span className="badge" style={{ backgroundColor: '#f3e8ff', color: '#6b21a8' }}>
          <Shield size={12} /> Admin
        </span>
      );
    }
    if (role === 'SUPPORT_AGENT') {
      return (
        <span className="badge" style={{ backgroundColor: '#dbeafe', color: '#1e40af' }}>
          <Headphones size={12} /> Support Agent
        </span>
      );
    }
    return (
      <span className="badge" style={{ backgroundColor: '#f1f5f9', color: '#475569' }}>
        <User size={12} /> Employee
      </span>
    );
  };

  return (
    <div className="page-body">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
            User & Agent Directory
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
            Manage staff accounts, support agents, and role authorization permissions.
          </p>
        </div>

        <button className="btn btn-primary" onClick={() => setIsCreateOpen(true)}>
          <UserPlus size={16} /> Add User / Agent
        </button>
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px 20px' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: '1 1 240px' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search by name or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '36px' }}
            />
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
          </div>

          <select
            className="form-select"
            value={roleFilter}
            onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
            style={{ width: 'auto', flex: '0 1 160px' }}
          >
            <option value="">All Roles</option>
            <option value="EMPLOYEE">Employees</option>
            <option value="SUPPORT_AGENT">Support Agents</option>
            <option value="ADMIN">Administrators</option>
          </select>

          <select
            className="form-select"
            value={activeFilter}
            onChange={(e) => { setActiveFilter(e.target.value); setPage(1); }}
            style={{ width: 'auto', flex: '0 1 150px' }}
          >
            <option value="">All Statuses</option>
            <option value="true">Active Only</option>
            <option value="false">Deactivated</option>
          </select>

          <button type="submit" className="btn btn-primary" style={{ padding: '8px 16px' }}>
            Filter
          </button>
        </form>
      </div>

      {/* Users Table */}
      <div className="card" style={{ padding: 0 }}>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>User Details</th>
                <th>Role</th>
                <th>Account Status</th>
                <th>Registered On</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{u.name}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{u.email}</div>
                  </td>
                  <td>{getRoleBadge(u.role)}</td>
                  <td>
                    {u.is_active ? (
                      <span className="badge" style={{ backgroundColor: '#ecfdf5', color: '#047857' }}>
                        <CheckCircle size={12} /> Active
                      </span>
                    ) : (
                      <span className="badge" style={{ backgroundColor: '#fef2f2', color: '#b91c1c' }}>
                        <XCircle size={12} /> Deactivated
                      </span>
                    )}
                  </td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      className={`btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-success'}`}
                      style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                      onClick={() => {
                        setTargetUser(u);
                        setIsConfirmOpen(true);
                      }}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="pagination-container">
          <div>
            Showing <strong>{users.length > 0 ? (page - 1) * pageSize + 1 : 0}</strong> to{' '}
            <strong>{Math.min(page * pageSize, total)}</strong> of <strong>{total}</strong> users
          </div>

          <div className="pagination-buttons">
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || loading}
            >
              <ChevronLeft size={16} /> Prev
            </button>
            <span style={{ display: 'flex', alignItems: 'center', padding: '0 10px', fontSize: '0.85rem' }}>
              Page {page} of {totalPages}
            </span>
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || loading}
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Confirm Deactivate / Activate Dialog */}
      {targetUser && (
        <ConfirmDialog
          isOpen={isConfirmOpen}
          onClose={() => setIsConfirmOpen(false)}
          onConfirm={handleToggleStatus}
          title={`${targetUser.is_active ? 'Deactivate' : 'Activate'} User Account`}
          message={`Are you sure you want to ${targetUser.is_active ? 'deactivate' : 'reactivate'} the account for "${targetUser.name}" (${targetUser.email})?`}
          confirmText={targetUser.is_active ? 'Deactivate' : 'Activate'}
          isDestructive={targetUser.is_active}
          loading={toggleLoading}
        />
      )}

      {/* Create User / Agent Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Create New User or Support Agent"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleCreateUser} disabled={createLoading}>
              {createLoading ? 'Creating...' : 'Create Account'}
            </button>
          </>
        }
      >
        <form onSubmit={handleCreateUser}>
          <div className="form-group">
            <label className="form-label">Full Name *</label>
            <input
              type="text"
              required
              className="form-input"
              placeholder="e.g. Michael Scott"
              value={createForm.name}
              onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address *</label>
            <input
              type="email"
              required
              className="form-input"
              placeholder="e.g. m.scott@trackit.internal"
              value={createForm.email}
              onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Temporary Password *</label>
            <input
              type="password"
              required
              minLength={6}
              className="form-input"
              placeholder="••••••••"
              value={createForm.password}
              onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Assigned Role *</label>
            <select
              className="form-select"
              value={createForm.role}
              onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
            >
              <option value="SUPPORT_AGENT">SUPPORT_AGENT (Triage & Resolve Tickets)</option>
              <option value="EMPLOYEE">EMPLOYEE (Standard Staff Member)</option>
              <option value="ADMIN">ADMIN (Full Administrative Control)</option>
            </select>
          </div>
        </form>
      </Modal>
    </div>
  );
};

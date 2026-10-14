import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ticketService } from '../services/ticketService';
import { categoryService } from '../services/categoryService';
import { userService } from '../services/userService';
import { TicketTable } from '../components/TicketTable';
import { ErrorMessage } from '../components/ErrorMessage';
import {
  Search,
  Filter,
  PlusCircle,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
} from 'lucide-react';

export const TicketsList = () => {
  const navigate = useNavigate();
  const { isEmployee, isSupportOrAdmin } = useAuth();

  const [tickets, setTickets] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);

  // Filters
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [assignedTo, setAssignedTo] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  // Metadata for filter dropdowns
  const [categories, setCategories] = useState([]);
  const [agents, setAgents] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    categoryService.listCategories().then((res) => setCategories(res || []));
    if (isSupportOrAdmin) {
      userService.getAgents().then((res) => setAgents(res || []));
    }
  }, [isSupportOrAdmin]);

  const fetchTickets = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      if (search.trim()) params.search = search.trim();
      if (status) params.status = status;
      if (priority) params.priority = priority;
      if (categoryId) params.category_id = Number(categoryId);
      if (assignedTo && isSupportOrAdmin) params.assigned_to = Number(assignedTo);

      const res = await ticketService.listTickets(params);
      setTickets(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err) {
      setError(err.message || 'Failed to fetch tickets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [page, pageSize, status, priority, categoryId, assignedTo, sortBy, sortOrder]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchTickets();
  };

  const handleResetFilters = () => {
    setSearch('');
    setStatus('');
    setPriority('');
    setCategoryId('');
    setAssignedTo('');
    setSortBy('created_at');
    setSortOrder('desc');
    setPage(1);
  };

  return (
    <div className="page-body">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
            {isEmployee ? 'My Reported Tickets' : 'IT Service Ticket Directory'}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
            {isEmployee
              ? 'Track progress and status updates for your service requests'
              : 'Search, triage, and filter organization support issues'}
          </p>
        </div>

        <button className="btn btn-primary" onClick={() => navigate('/tickets/create')}>
          <PlusCircle size={16} /> Raise Ticket
        </button>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchTickets} />}

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px 20px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
          {/* Search Input */}
          <div style={{ position: 'relative', flex: '1 1 240px' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search by title, description or #ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '36px' }}
            />
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
          </div>

          {/* Status Filter */}
          <select
            className="form-select"
            value={status}
            onChange={(e) => { setStatus(e.target.value); setPage(1); }}
            style={{ width: 'auto', flex: '0 1 150px' }}
          >
            <option value="">All Statuses</option>
            <option value="OPEN">OPEN</option>
            <option value="ASSIGNED">ASSIGNED</option>
            <option value="IN_PROGRESS">IN_PROGRESS</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="CLOSED">CLOSED</option>
            <option value="REOPENED">REOPENED</option>
          </select>

          {/* Priority Filter */}
          <select
            className="form-select"
            value={priority}
            onChange={(e) => { setPriority(e.target.value); setPage(1); }}
            style={{ width: 'auto', flex: '0 1 140px' }}
          >
            <option value="">All Priorities</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>

          {/* Category Filter */}
          <select
            className="form-select"
            value={categoryId}
            onChange={(e) => { setCategoryId(e.target.value); setPage(1); }}
            style={{ width: 'auto', flex: '0 1 150px' }}
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>

          {/* Assigned Agent Filter (for Support Agents / Admin) */}
          {isSupportOrAdmin && (
            <select
              className="form-select"
              value={assignedTo}
              onChange={(e) => { setAssignedTo(e.target.value); setPage(1); }}
              style={{ width: 'auto', flex: '0 1 160px' }}
            >
              <option value="">All Assignees</option>
              {agents.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          )}

          {/* Sorting Control */}
          <select
            className="form-select"
            value={`${sortBy}:${sortOrder}`}
            onChange={(e) => {
              const [sb, so] = e.target.value.split(':');
              setSortBy(sb);
              setSortOrder(so);
              setPage(1);
            }}
            style={{ width: 'auto', flex: '0 1 160px' }}
          >
            <option value="created_at:desc">Newest First</option>
            <option value="created_at:asc">Oldest First</option>
            <option value="priority:desc">Priority (High-Low)</option>
            <option value="due_at:asc">SLA Due Soonest</option>
          </select>

          <button type="submit" className="btn btn-primary" style={{ padding: '8px 14px' }}>
            Filter
          </button>

          {(search || status || priority || categoryId || assignedTo) && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleResetFilters}
              title="Reset all filters"
              style={{ padding: '8px 12px' }}
            >
              <RotateCcw size={15} />
            </button>
          )}
        </form>
      </div>

      {/* Ticket List Table */}
      <div className="card" style={{ padding: 0 }}>
        <TicketTable tickets={tickets} loading={loading} />

        {/* Pagination Bar */}
        <div className="pagination-container">
          <div>
            Showing <strong>{tickets.length > 0 ? (page - 1) * pageSize + 1 : 0}</strong> to{' '}
            <strong>{Math.min(page * pageSize, total)}</strong> of <strong>{total}</strong> tickets
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
    </div>
  );
};

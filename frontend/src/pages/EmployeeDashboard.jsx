import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { dashboardService } from '../services/dashboardService';
import { ticketService } from '../services/ticketService';
import { StatCard } from '../components/StatCard';
import { TicketTable } from '../components/TicketTable';
import { ErrorMessage } from '../components/ErrorMessage';
import { PlusCircle, Ticket, Clock, CheckCircle2, RotateCcw } from 'lucide-react';

export const EmployeeDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [recentTickets, setRecentTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumData, ticketsData] = await Promise.all([
        dashboardService.getSummary(),
        ticketService.listTickets({ page: 1, page_size: 5, sort_by: 'created_at', sort_order: 'desc' }),
      ]);
      setSummary(sumData);
      setRecentTickets(ticketsData.items || []);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="page-body">
      {/* Welcome Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '28px',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
            Welcome back, {user?.name?.split(' ')[0] || 'Team Member'} 👋
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Here is the live status of your reported IT issues and requests.
          </p>
        </div>

        <button
          className="btn btn-primary"
          onClick={() => navigate('/tickets/create')}
          style={{ padding: '10px 20px', fontSize: '0.95rem' }}
        >
          <PlusCircle size={18} /> Raise New Support Ticket
        </button>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchDashboardData} />}

      {/* KPI Stats Grid */}
      <div className="stats-grid">
        <StatCard
          title="Total Raised"
          value={summary?.total_tickets ?? 0}
          subtitle="All tickets submitted by you"
          icon={Ticket}
          color="blue"
        />
        <StatCard
          title="Open Issues"
          value={summary?.open_tickets ?? 0}
          subtitle="Waiting in triage queue"
          icon={Clock}
          color="amber"
        />
        <StatCard
          title="In Progress"
          value={summary?.in_progress_tickets ?? 0}
          subtitle="Currently being investigated"
          icon={Clock}
          color="indigo"
        />
        <StatCard
          title="Resolved / Closed"
          value={(summary?.resolved_tickets || 0) + (summary?.closed_tickets || 0)}
          subtitle="Completed successfully"
          icon={CheckCircle2}
          color="green"
        />
      </div>

      {/* Recent Tickets Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Recent Tickets</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Your latest submitted service requests
            </p>
          </div>
          <button
            className="btn btn-sm btn-secondary"
            onClick={() => navigate('/tickets')}
          >
            View All My Tickets
          </button>
        </div>

        <TicketTable tickets={recentTickets} loading={loading} />
      </div>
    </div>
  );
};

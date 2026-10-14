import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { dashboardService } from '../services/dashboardService';
import { ticketService } from '../services/ticketService';
import { StatCard } from '../components/StatCard';
import { TicketTable } from '../components/TicketTable';
import { ErrorMessage } from '../components/ErrorMessage';
import {
  Inbox,
  Clock,
  AlertTriangle,
  Flame,
  CheckCircle,
  Timer,
  Layers,
} from 'lucide-react';

export const AgentDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [activeTab, setActiveTab] = useState('assigned'); // 'assigned' | 'unassigned'
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const sum = await dashboardService.getSummary();
      setSummary(sum);

      const params = {
        page: 1,
        page_size: 10,
        sort_by: 'created_at',
        sort_order: 'desc',
      };

      if (activeTab === 'assigned') {
        params.assigned_to = user.id;
      } else {
        params.status = 'OPEN';
      }

      const tData = await ticketService.listTickets(params);
      setTickets(tData.items || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch agent dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [activeTab]);

  return (
    <div className="page-body">
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
          Support Agent Workbench
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
          Live service triage queue, SLA status tracking, and active assignments.
        </p>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchDashboard} />}

      {/* KPI Stats Grid */}
      <div className="stats-grid">
        <StatCard
          title="Assigned to Me"
          value={summary?.total_tickets ?? 0}
          subtitle="Tickets in your personal queue"
          icon={Inbox}
          color="blue"
        />
        <StatCard
          title="In Progress"
          value={summary?.in_progress_tickets ?? 0}
          subtitle="Under active investigation"
          icon={Clock}
          color="indigo"
        />
        <StatCard
          title="SLA At Risk"
          value={summary?.sla_at_risk_count ?? 0}
          subtitle="Deadline approaching (< 4h)"
          icon={AlertTriangle}
          color="amber"
        />
        <StatCard
          title="SLA Breached"
          value={summary?.sla_breached_count ?? 0}
          subtitle="Past response/resolution window"
          icon={Flame}
          color="red"
        />
        <StatCard
          title="Avg Resolution"
          value={`${summary?.avg_resolution_time_hours ?? 0}h`}
          subtitle="Average turnaround duration"
          icon={Timer}
          color="green"
        />
      </div>

      {/* Ticket Work Queue Card */}
      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className={`btn btn-sm ${activeTab === 'assigned' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('assigned')}
            >
              My Assigned Queue
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'unassigned' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('unassigned')}
            >
              Unassigned Incoming (OPEN)
            </button>
          </div>

          <button
            className="btn btn-sm btn-secondary"
            onClick={() => navigate('/tickets')}
          >
            <Layers size={14} /> Full Ticket Directory
          </button>
        </div>

        <TicketTable tickets={tickets} loading={loading} />
      </div>
    </div>
  );
};

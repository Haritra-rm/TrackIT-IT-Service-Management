import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService } from '../services/dashboardService';
import { ticketService } from '../services/ticketService';
import { StatCard } from '../components/StatCard';
import { TicketTable } from '../components/TicketTable';
import { ErrorMessage } from '../components/ErrorMessage';
import { PriorityBadge } from '../components/PriorityBadge';
import { StatusBadge } from '../components/StatusBadge';
import {
  ShieldAlert,
  Clock,
  CheckCircle2,
  Flame,
  Timer,
  TrendingUp,
  Users,
  FolderKanban,
  BarChart2,
} from 'lucide-react';

export const AdminDashboard = () => {
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [statusCounts, setStatusCounts] = useState([]);
  const [priorityCounts, setPriorityCounts] = useState([]);
  const [categoryCounts, setCategoryCounts] = useState([]);
  const [agentMetrics, setAgentMetrics] = useState([]);
  const [recentTickets, setRecentTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAdminData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sum, sc, pc, cc, am, tickets] = await Promise.all([
        dashboardService.getSummary(),
        dashboardService.getTicketsByStatus(),
        dashboardService.getTicketsByPriority(),
        dashboardService.getTicketsByCategory(),
        dashboardService.getAgentPerformance(),
        ticketService.listTickets({ page: 1, page_size: 5, sort_by: 'created_at', sort_order: 'desc' }),
      ]);
      setSummary(sum);
      setStatusCounts(sc || []);
      setPriorityCounts(pc || []);
      setCategoryCounts(cc || []);
      setAgentMetrics(am || []);
      setRecentTickets(tickets.items || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch admin system metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  return (
    <div className="page-body">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
            IT Operations & Executive Command Center
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            Enterprise-wide real-time service health, SLA compliance, and agent performance.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/reports')}>
            <BarChart2 size={16} /> Detailed Analytics
          </button>
          <button className="btn btn-primary" onClick={() => navigate('/users')}>
            <Users size={16} /> Manage Users
          </button>
        </div>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchAdminData} />}

      {/* Primary KPI Grid */}
      <div className="stats-grid">
        <StatCard
          title="Total Tickets"
          value={summary?.total_tickets ?? 0}
          subtitle="All recorded organization issues"
          icon={FolderKanban}
          color="blue"
        />
        <StatCard
          title="Open Triage"
          value={summary?.open_tickets ?? 0}
          subtitle="Awaiting initial assignment"
          icon={Clock}
          color="amber"
        />
        <StatCard
          title="In Progress"
          value={summary?.in_progress_tickets ?? 0}
          subtitle="Actively being resolved"
          icon={TrendingUp}
          color="indigo"
        />
        <StatCard
          title="Resolved Rate"
          value={`${summary?.resolution_rate ?? 0}%`}
          subtitle={`${summary?.resolved_tickets || 0} resolved + ${summary?.closed_tickets || 0} closed`}
          icon={CheckCircle2}
          color="green"
        />
        <StatCard
          title="SLA Breached"
          value={summary?.sla_breached_count ?? 0}
          subtitle={`${summary?.sla_breach_rate ?? 0}% organization breach rate`}
          icon={Flame}
          color="red"
        />
        <StatCard
          title="Avg Resolution"
          value={`${summary?.avg_resolution_time_hours ?? 0}h`}
          subtitle={`Avg 1st Response: ${summary?.avg_first_response_time_hours ?? 0}h`}
          icon={Timer}
          color="purple"
        />
      </div>

      {/* Distribution Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        {/* Status Distribution */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '16px' }}>Tickets by Lifecycle Status</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {statusCounts.map((sc) => (
              <div key={sc.status}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                  <StatusBadge status={sc.status} />
                  <span style={{ fontWeight: 600 }}>{sc.count} ({sc.percentage}%)</span>
                </div>
                <div style={{ width: '100%', height: '6px', backgroundColor: '#f1f5f9', borderRadius: '3px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${sc.percentage}%`,
                      height: '100%',
                      backgroundColor: '#3b82f6',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Distribution */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '16px' }}>Tickets by Severity Priority</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {priorityCounts.map((pc) => (
              <div key={pc.priority}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                  <PriorityBadge priority={pc.priority} />
                  <span style={{ fontWeight: 600 }}>{pc.count} ({pc.percentage}%)</span>
                </div>
                <div style={{ width: '100%', height: '6px', backgroundColor: '#f1f5f9', borderRadius: '3px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${pc.percentage}%`,
                      height: '100%',
                      backgroundColor: pc.priority === 'CRITICAL' ? '#ef4444' : pc.priority === 'HIGH' ? '#f97316' : '#3b82f6',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Support Agent Performance Table */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <div>
            <h2 className="card-title">Support Agent Workload & Performance</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Individual agent throughput and SLA compliance ratings
            </p>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Agent</th>
                <th>Assigned Active</th>
                <th>In Progress</th>
                <th>Resolved</th>
                <th>Avg Turnaround</th>
                <th>SLA Compliance</th>
              </tr>
            </thead>
            <tbody>
              {agentMetrics.map((agent) => (
                <tr key={agent.agent_id}>
                  <td>
                    <div style={{ fontWeight: 600 }}>{agent.agent_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{agent.agent_email}</div>
                  </td>
                  <td>
                    <span style={{ fontWeight: 600 }}>{agent.assigned_count}</span>
                  </td>
                  <td>{agent.in_progress_count}</td>
                  <td>
                    <span style={{ color: '#059669', fontWeight: 600 }}>{agent.resolved_count}</span>
                  </td>
                  <td>{agent.avg_resolution_hours}h</td>
                  <td>
                    <span
                      style={{
                        padding: '3px 8px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        backgroundColor: agent.sla_compliance_rate >= 80 ? '#ecfdf5' : '#fef2f2',
                        color: agent.sla_compliance_rate >= 80 ? '#047857' : '#b91c1c',
                      }}
                    >
                      {agent.sla_compliance_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Activity Tickets */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Tickets Across Organization</h2>
          <button className="btn btn-sm btn-secondary" onClick={() => navigate('/tickets')}>
            View All in Ticket Directory
          </button>
        </div>
        <TicketTable tickets={recentTickets} loading={loading} />
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/dashboardService';
import { StatCard } from '../components/StatCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';
import {
  BarChart3,
  Flame,
  CheckCircle2,
  Clock,
  Timer,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
);

export const Reports = () => {
  const [summary, setSummary] = useState(null);
  const [statusData, setStatusData] = useState([]);
  const [priorityData, setPriorityData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [agentMetrics, setAgentMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const [sum, st, pr, cat, ag] = await Promise.all([
          dashboardService.getSummary(),
          dashboardService.getTicketsByStatus(),
          dashboardService.getTicketsByPriority(),
          dashboardService.getTicketsByCategory(),
          dashboardService.getAgentPerformance(),
        ]);
        setSummary(sum);
        setStatusData(st || []);
        setPriorityData(pr || []);
        setCategoryData(cat || []);
        setAgentMetrics(ag || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch analytics metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Calculating operational KPIs and charts..." />;
  }

  // Chart 1: Status Doughnut
  const doughnutData = {
    labels: statusData.map((s) => s.status),
    datasets: [
      {
        data: statusData.map((s) => s.count),
        backgroundColor: [
          '#3b82f6', // OPEN
          '#f59e0b', // ASSIGNED
          '#6366f1', // IN_PROGRESS
          '#10b981', // RESOLVED
          '#64748b', // CLOSED
          '#f43f5e', // REOPENED
        ],
        borderWidth: 1,
      },
    ],
  };

  // Chart 2: Priority Bar Chart
  const priorityChartData = {
    labels: priorityData.map((p) => p.priority),
    datasets: [
      {
        label: 'Tickets by Priority',
        data: priorityData.map((p) => p.count),
        backgroundColor: [
          '#94a3b8', // LOW
          '#3b82f6', // MEDIUM
          '#f97316', // HIGH
          '#ef4444', // CRITICAL
        ],
        borderRadius: 6,
      },
    ],
  };

  // Chart 3: Category Breakdown Bar Chart
  const categoryChartData = {
    labels: categoryData.map((c) => c.category_name),
    datasets: [
      {
        label: 'Issues Reported',
        data: categoryData.map((c) => c.count),
        backgroundColor: '#2563eb',
        borderRadius: 6,
      },
    ],
  };

  return (
    <div className="page-body">
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
          Service Performance Analytics & KPI Dashboard
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
          Comprehensive operational metrics calculated in real-time from the organization database.
        </p>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* KPI Grid */}
      <div className="stats-grid">
        <StatCard
          title="Total Issues"
          value={summary?.total_tickets ?? 0}
          subtitle="Processed across departments"
          icon={BarChart3}
          color="blue"
        />
        <StatCard
          title="Resolution Rate"
          value={`${summary?.resolution_rate ?? 0}%`}
          subtitle="Resolved / Total tickets"
          icon={CheckCircle2}
          color="green"
        />
        <StatCard
          title="SLA Breach Rate"
          value={`${summary?.sla_breach_rate ?? 0}%`}
          subtitle={`${summary?.sla_breached_count ?? 0} breached tickets`}
          icon={Flame}
          color="red"
        />
        <StatCard
          title="Avg Turnaround"
          value={`${summary?.avg_resolution_time_hours ?? 0}h`}
          subtitle="Time to resolution"
          icon={Timer}
          color="purple"
        />
        <StatCard
          title="Avg 1st Response"
          value={`${summary?.avg_first_response_time_hours ?? 0}h`}
          subtitle="Initial triage response"
          icon={Clock}
          color="indigo"
        />
      </div>

      {/* Visual Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '28px' }}>
        {/* Doughnut: Status Distribution */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '16px' }}>Tickets by Lifecycle Status</h2>
          <div style={{ maxWidth: '280px', width: '100%', margin: '0 auto', padding: '12px 0' }}>
            <Doughnut data={doughnutData} options={{ maintainAspectRatio: true, plugins: { legend: { position: 'bottom' } } }} />
          </div>
        </div>

        {/* Bar: Priority Distribution */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '16px' }}>Ticket Severity Distribution</h2>
          <div style={{ height: '280px' }}>
            <Bar
              data={priorityChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
              }}
            />
          </div>
        </div>

        {/* Bar: Category Distribution */}
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h2 className="card-title" style={{ marginBottom: '16px' }}>Volume by Problem Category</h2>
          <div style={{ height: '260px' }}>
            <Bar
              data={categoryChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
              }}
            />
          </div>
        </div>
      </div>

      {/* Agent Performance Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Agent SLA Compliance & Resolution Benchmarks</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Individual agent metrics evaluated against strict organizational SLA targets.
            </p>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Support Agent</th>
                <th>Assigned Count</th>
                <th>In Progress</th>
                <th>Resolved Count</th>
                <th>Avg Turnaround Time</th>
                <th>SLA Compliance Score</th>
              </tr>
            </thead>
            <tbody>
              {agentMetrics.map((ag) => (
                <tr key={ag.agent_id}>
                  <td>
                    <div style={{ fontWeight: 600 }}>{ag.agent_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{ag.agent_email}</div>
                  </td>
                  <td>{ag.assigned_count}</td>
                  <td>{ag.in_progress_count}</td>
                  <td>
                    <span style={{ color: '#059669', fontWeight: 600 }}>{ag.resolved_count}</span>
                  </td>
                  <td>{ag.avg_resolution_hours} hours</td>
                  <td>
                    <span
                      style={{
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.8rem',
                        fontWeight: 700,
                        backgroundColor: ag.sla_compliance_rate >= 80 ? '#ecfdf5' : '#fef2f2',
                        color: ag.sla_compliance_rate >= 80 ? '#047857' : '#b91c1c',
                      }}
                    >
                      {ag.sla_compliance_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

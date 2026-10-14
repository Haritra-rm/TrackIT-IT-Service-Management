import React from 'react';
import { useNavigate } from 'react-router-dom';
import { StatusBadge } from './StatusBadge';
import { PriorityBadge } from './PriorityBadge';
import { SlaBadge } from './SlaBadge';
import { ChevronRight, Inbox } from 'lucide-react';

export const TicketTable = ({ tickets = [], loading = false }) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="table-container" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
        Loading tickets...
      </div>
    );
  }

  if (!tickets || tickets.length === 0) {
    return (
      <div
        className="table-container"
        style={{
          padding: '60px 20px',
          textAlign: 'center',
          color: '#64748b',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div style={{ backgroundColor: '#f1f5f9', padding: '16px', borderRadius: '50%', marginBottom: '12px' }}>
          <Inbox size={36} color="#94a3b8" />
        </div>
        <div style={{ fontSize: '1rem', fontWeight: 600, color: '#334155' }}>No tickets found</div>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
          There are no issues matching your current search or filter criteria.
        </p>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: '80px' }}>ID</th>
            <th>Title & Category</th>
            <th>Priority</th>
            <th>Status</th>
            <th>SLA Status</th>
            <th>Creator</th>
            <th>Assigned To</th>
            <th>Created</th>
            <th style={{ width: '50px' }}></th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr
              key={ticket.id}
              onClick={() => navigate(`/tickets/${ticket.id}`)}
              style={{ cursor: 'pointer' }}
            >
              <td>
                <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 600, color: 'var(--primary)' }}>
                  #{ticket.id}
                </span>
              </td>
              <td>
                <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '2px' }}>
                  {ticket.title}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {ticket.category_name || 'General'}
                </div>
              </td>
              <td>
                <PriorityBadge priority={ticket.priority} />
              </td>
              <td>
                <StatusBadge status={ticket.status} />
              </td>
              <td>
                <SlaBadge
                  slaStatus={ticket.sla_status}
                  remainingHours={ticket.sla_remaining_hours}
                  isBreached={ticket.is_breached}
                />
              </td>
              <td>
                <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>
                  {ticket.creator_name || 'Anonymous'}
                </div>
              </td>
              <td>
                <div style={{ fontSize: '0.85rem', color: ticket.assignee_name ? 'var(--text-main)' : 'var(--text-light)' }}>
                  {ticket.assignee_name || 'Unassigned'}
                </div>
              </td>
              <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'N/A'}
              </td>
              <td>
                <ChevronRight size={18} color="#94a3b8" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

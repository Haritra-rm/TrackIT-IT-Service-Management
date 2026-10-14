import React from 'react';
import { useNavigate } from 'react-router-dom';
import { StatusBadge } from './StatusBadge';
import { PriorityBadge } from './PriorityBadge';
import { SlaBadge } from './SlaBadge';
import { ChevronRight, Inbox, PlusCircle } from 'lucide-react';

export const TicketTable = ({ tickets = [], loading = false }) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="table-container" style={{ padding: '36px 20px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          <div
            style={{
              width: '18px',
              height: '18px',
              border: '2px solid #cbd5e1',
              borderTopColor: 'var(--primary)',
              borderRadius: '50%',
              animation: 'spin 0.8s linear infinite',
            }}
          />
          <span>Loading ticket records from directory...</span>
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!tickets || tickets.length === 0) {
    return (
      <div
        className="table-container"
        style={{
          padding: '64px 24px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#ffffff',
        }}
      >
        <div
          style={{
            width: '64px',
            height: '64px',
            backgroundColor: 'var(--slate-100)',
            borderRadius: 'var(--radius-full)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '16px',
            boxShadow: 'var(--shadow-xs)',
          }}
        >
          <Inbox size={32} color="var(--slate-400)" />
        </div>
        <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--slate-800)', letterSpacing: '-0.01em' }}>
          No support tickets found
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px', maxWidth: '380px' }}>
          There are currently no tickets matching your active filter criteria or queue assignments.
        </p>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: '85px' }}>Ticket ID</th>
            <th>Title & Category</th>
            <th>Priority</th>
            <th>Status</th>
            <th>SLA Target</th>
            <th>Requested By</th>
            <th>Assigned Agent</th>
            <th>Created</th>
            <th style={{ width: '40px' }} aria-label="Actions"></th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr
              key={ticket.id}
              onClick={() => navigate(`/tickets/${ticket.id}`)}
              style={{ cursor: 'pointer' }}
              title={`View details for ticket #${ticket.id}`}
            >
              <td>
                <span
                  style={{
                    fontFamily: 'JetBrains Mono',
                    fontWeight: 700,
                    fontSize: '0.82rem',
                    color: 'var(--primary)',
                    backgroundColor: 'var(--primary-light)',
                    padding: '3px 7px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--primary-border)',
                  }}
                >
                  #{ticket.id}
                </span>
              </td>
              <td style={{ minWidth: '220px', maxWidth: '340px' }}>
                <div
                  style={{
                    fontWeight: 600,
                    color: 'var(--text-main)',
                    marginBottom: '3px',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {ticket.title}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                  {ticket.category_name || 'General Issue'}
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
                <div style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-main)' }}>
                  {ticket.creator_name || 'Anonymous'}
                </div>
              </td>
              <td>
                <div
                  style={{
                    fontSize: '0.85rem',
                    color: ticket.assignee_name ? 'var(--text-main)' : 'var(--text-light)',
                    fontStyle: ticket.assignee_name ? 'normal' : 'italic',
                  }}
                >
                  {ticket.assignee_name || 'Unassigned'}
                </div>
              </td>
              <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'N/A'}
              </td>
              <td style={{ textAlign: 'right', paddingRight: '12px' }}>
                <ChevronRight size={18} color="var(--slate-400)" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

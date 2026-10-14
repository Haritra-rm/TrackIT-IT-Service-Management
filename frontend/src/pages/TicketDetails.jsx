import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ticketService } from '../services/ticketService';
import { intelligenceService } from '../services/intelligenceService';
import { userService } from '../services/userService';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { SlaBadge } from '../components/SlaBadge';
import { Modal } from '../components/Modal';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import {
  ArrowLeft,
  User,
  Clock,
  Calendar,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  MessageSquare,
  History,
  Send,
  UserPlus,
  ArrowRightCircle,
  CheckSquare,
  RotateCcw,
  Trash2,
  FileCheck,
  Sparkles,
  ShieldAlert,
  Layers,
  ExternalLink,
} from 'lucide-react';

export const TicketDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isEmployee, isSupportOrAdmin, isAdmin } = useAuth();

  const [ticket, setTicket] = useState(null);
  const [comments, setComments] = useState([]);
  const [history, setHistory] = useState([]);
  const [agents, setAgents] = useState([]);

  // Intelligence State (Related Tickets & Escalation Assessment)
  const [relatedTickets, setRelatedTickets] = useState([]);
  const [relatedLoading, setRelatedLoading] = useState(true);
  const [escalation, setEscalation] = useState(null);
  const [escalationLoading, setEscalationLoading] = useState(true);

  const [newComment, setNewComment] = useState('');
  const [commentLoading, setCommentLoading] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modals state
  const [isAssignOpen, setIsAssignOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('');

  const [isStatusOpen, setIsStatusOpen] = useState(false);
  const [nextStatus, setNextStatus] = useState('');

  const [isResolveOpen, setIsResolveOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');

  const [isReopenOpen, setIsReopenOpen] = useState(false);
  const [reopenReason, setReopenReason] = useState('');

  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchTicketData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [tData, cData, hData] = await Promise.all([
        ticketService.getTicket(id),
        ticketService.getComments(id),
        ticketService.getHistory(id),
      ]);
      setTicket(tData);
      setComments(cData || []);
      setHistory(hData || []);

      if (isSupportOrAdmin) {
        userService.getAgents().then((ag) => setAgents(ag || []));
      }

      // Fetch Incident Intelligence in parallel
      setRelatedLoading(true);
      setEscalationLoading(true);
      intelligenceService.getRelatedTickets(id)
        .then((res) => setRelatedTickets(res?.related_tickets || []))
        .catch((e) => console.debug('Related tickets error:', e))
        .finally(() => setRelatedLoading(false));

      intelligenceService.getEscalationAssessment(id)
        .then((res) => setEscalation(res))
        .catch((e) => console.debug('Escalation error:', e))
        .finally(() => setEscalationLoading(false));
    } catch (err) {
      setError(err.message || 'Failed to load ticket details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTicketData();
  }, [id]);

  const handlePostComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setCommentLoading(true);
    try {
      const added = await ticketService.addComment(ticket.id, newComment.trim());
      setComments((prev) => [...prev, added]);
      setNewComment('');
    } catch (err) {
      setError(err.message || 'Failed to post comment');
    } finally {
      setCommentLoading(false);
    }
  };

  const handleAssign = async () => {
    if (!selectedAgent) return;
    setActionLoading(true);
    try {
      const updated = await ticketService.assignTicket(ticket.id, Number(selectedAgent));
      setTicket(updated);
      setIsAssignOpen(false);
      // Refresh history & comments
      const [cData, hData] = await Promise.all([
        ticketService.getComments(id),
        ticketService.getHistory(id),
      ]);
      setComments(cData);
      setHistory(hData);
    } catch (err) {
      setError(err.message || 'Failed to assign ticket');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!nextStatus) return;
    setActionLoading(true);
    try {
      const updated = await ticketService.updateStatus(ticket.id, nextStatus);
      setTicket(updated);
      setIsStatusOpen(false);
      const [cData, hData] = await Promise.all([
        ticketService.getComments(id),
        ticketService.getHistory(id),
      ]);
      setComments(cData);
      setHistory(hData);
    } catch (err) {
      setError(err.message || 'Failed to update status');
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!resolutionNotes.trim()) return;
    setActionLoading(true);
    try {
      const updated = await ticketService.resolveTicket(ticket.id, resolutionNotes.trim());
      setTicket(updated);
      setIsResolveOpen(false);
      setResolutionNotes('');
      const [cData, hData] = await Promise.all([
        ticketService.getComments(id),
        ticketService.getHistory(id),
      ]);
      setComments(cData);
      setHistory(hData);
    } catch (err) {
      setError(err.message || 'Failed to resolve ticket');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReopen = async () => {
    if (!reopenReason.trim()) return;
    setActionLoading(true);
    try {
      const updated = await ticketService.reopenTicket(ticket.id, reopenReason.trim());
      setTicket(updated);
      setIsReopenOpen(false);
      setReopenReason('');
      const [cData, hData] = await Promise.all([
        ticketService.getComments(id),
        ticketService.getHistory(id),
      ]);
      setComments(cData);
      setHistory(hData);
    } catch (err) {
      setError(err.message || 'Failed to reopen ticket');
    } finally {
      setActionLoading(false);
    }
  };

  const handleClose = async () => {
    setActionLoading(true);
    try {
      const updated = await ticketService.closeTicket(ticket.id);
      setTicket(updated);
      const [cData, hData] = await Promise.all([
        ticketService.getComments(id),
        ticketService.getHistory(id),
      ]);
      setComments(cData);
      setHistory(hData);
    } catch (err) {
      setError(err.message || 'Failed to close ticket');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    setActionLoading(true);
    try {
      await ticketService.deleteTicket(ticket.id);
      navigate('/tickets');
    } catch (err) {
      setError(err.message || 'Failed to delete ticket');
      setIsDeleteOpen(false);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading ticket details & audit history..." />;
  }

  if (!ticket && error) {
    return (
      <div className="page-body" style={{ maxWidth: '800px' }}>
        <ErrorMessage message={error} />
        <button className="btn btn-secondary" onClick={() => navigate('/tickets')}>
          <ArrowLeft size={16} /> Return to Tickets
        </button>
      </div>
    );
  }

  const isCreator = Boolean(user && ticket && user.id === ticket.created_by);
  const steps = ['OPEN', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'];
  const currentStepIndex = steps.indexOf(ticket.status);

  return (
    <div className="page-body">
      {/* Top Bar Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <button className="btn btn-sm btn-secondary" onClick={() => navigate('/tickets')}>
          <ArrowLeft size={16} /> Back to Tickets
        </button>

        {/* Action Controls based on RBAC */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
          {isSupportOrAdmin && (
            <>
              {ticket.status !== 'CLOSED' && (
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => {
                    setSelectedAgent(ticket.assigned_to || '');
                    setIsAssignOpen(true);
                  }}
                >
                  <UserPlus size={15} /> {ticket.assigned_to ? 'Reassign Agent' : 'Assign Ticket'}
                </button>
              )}

              {ticket.status !== 'RESOLVED' && ticket.status !== 'CLOSED' && (
                <>
                  <button
                    className="btn btn-sm btn-secondary"
                    onClick={() => {
                      setNextStatus(ticket.status === 'OPEN' ? 'ASSIGNED' : 'IN_PROGRESS');
                      setIsStatusOpen(true);
                    }}
                  >
                    <ArrowRightCircle size={15} /> Update Status
                  </button>

                  <button
                    className="btn btn-sm btn-success"
                    onClick={() => setIsResolveOpen(true)}
                  >
                    <CheckSquare size={15} /> Resolve Issue
                  </button>
                </>
              )}
            </>
          )}

          {/* Close Action: Original Ticket Creator verifies and closes RESOLVED ticket */}
          {ticket.status === 'RESOLVED' && isCreator && (
            <button
              className="btn btn-sm btn-primary"
              onClick={handleClose}
              disabled={actionLoading}
              title="Verify resolution and close ticket"
            >
              <CheckCircle2 size={15} /> Close Ticket
            </button>
          )}

          {/* Reopen Action: Creator or Admin can reopen if RESOLVED or CLOSED */}
          {(ticket.status === 'RESOLVED' || ticket.status === 'CLOSED') && (
            <button
              className="btn btn-sm btn-secondary"
              onClick={() => setIsReopenOpen(true)}
              style={{ borderColor: '#f43f5e', color: '#e11d48' }}
              title="Reopen ticket if problem persists"
            >
              <RotateCcw size={15} /> Reopen Ticket
            </button>
          )}

          {isAdmin && (
            <button
              className="btn btn-sm btn-danger"
              onClick={() => setIsDeleteOpen(true)}
              title="Permanently Delete Ticket"
            >
              <Trash2 size={15} />
            </button>
          )}
        </div>
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Main Grid: Details on Left, Meta on Right */}
      <div className="ticket-details-layout" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(300px, 1fr)', gap: '24px' }}>
        {/* Left Column: Details, Comments, Timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Main Card */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
              <span style={{ fontFamily: 'JetBrains Mono', fontSize: '1rem', fontWeight: 800, color: 'var(--primary)', backgroundColor: 'var(--primary-light)', padding: '4px 10px', borderRadius: 'var(--radius-xs)', border: '1px solid var(--primary-border)' }}>
                TICKET #{ticket.id}
              </span>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <PriorityBadge priority={ticket.priority} />
                <StatusBadge status={ticket.status} />
              </div>
            </div>

            <h1 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '16px', lineHeight: 1.3 }}>
              {ticket.title}
            </h1>

            {/* Lifecycle Stepper */}
            {ticket.status !== 'REOPENED' ? (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  backgroundColor: 'var(--slate-50)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px 20px',
                  marginBottom: '20px',
                  overflowX: 'auto',
                  WebkitOverflowScrolling: 'touch',
                }}
              >
                {steps.map((st, idx) => {
                  const isDone = currentStepIndex >= idx;
                  const isCurrent = ticket.status === st;

                  return (
                    <React.Fragment key={st}>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px', minWidth: '60px' }}>
                        <div
                          style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '50%',
                            backgroundColor: isDone ? 'var(--primary)' : 'var(--slate-200)',
                            color: isDone ? '#fff' : 'var(--slate-600)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            boxShadow: isCurrent ? '0 0 0 3px rgba(37, 99, 235, 0.25)' : 'none',
                            transition: 'all var(--transition-fast)',
                          }}
                        >
                          {isDone ? '✓' : idx + 1}
                        </div>
                        <span
                          style={{
                            fontSize: '0.68rem',
                            fontWeight: isCurrent ? 700 : 600,
                            color: isCurrent ? 'var(--primary)' : 'var(--text-muted)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.04em',
                            textAlign: 'center',
                          }}
                        >
                          {st.replace('_', ' ')}
                        </span>
                      </div>
                      {idx < steps.length - 1 && (
                        <div
                          style={{
                            flex: 1,
                            height: '3px',
                            backgroundColor: currentStepIndex > idx ? 'var(--primary)' : 'var(--slate-200)',
                            margin: '0 8px',
                            minWidth: '16px',
                            borderRadius: '2px',
                          }}
                        />
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            ) : (
              <div
                style={{
                  backgroundColor: '#ffe4e6',
                  border: '1px solid #fecdd3',
                  borderRadius: 'var(--radius-sm)',
                  padding: '14px 18px',
                  color: '#9f1239',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  marginBottom: '20px',
                  fontSize: '0.88rem',
                }}
              >
                <RotateCcw size={18} />
                <strong>Ticket Reopened:</strong> The issue was flagged as persistent by the user after resolution.
              </div>
            )}

            <div style={{ fontSize: '0.95rem', color: '#334155', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
              {ticket.description}
            </div>

            {/* Resolution Notes Banner */}
            {ticket.resolution_notes && (
              <div
                style={{
                  marginTop: '24px',
                  padding: '16px 20px',
                  backgroundColor: '#ecfdf5',
                  border: '1px solid #a7f3d0',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#065f46', fontWeight: 700, marginBottom: '6px' }}>
                  <FileCheck size={18} /> Resolution Report
                </div>
                <p style={{ fontSize: '0.9rem', color: '#047857', whiteSpace: 'pre-wrap' }}>
                  {ticket.resolution_notes}
                </p>
                {ticket.resolved_at && (
                  <div style={{ fontSize: '0.75rem', color: '#059669', marginTop: '6px' }}>
                    Resolved on {new Date(ticket.resolved_at).toLocaleString()}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Incident Intelligence Section */}
          <div className="card" style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '8px', backgroundColor: '#e0e7ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Sparkles size={18} color="#4338ca" />
                </div>
                <div>
                  <h2 style={{ fontSize: '1.08rem', fontWeight: 700, color: 'var(--text-main)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                    Incident Intelligence
                  </h2>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Similarity-based related ticket analysis & objective rule-based escalation assessment
                  </span>
                </div>
              </div>
              <span style={{ fontSize: '0.72rem', padding: '3px 8px', borderRadius: '12px', backgroundColor: '#f1f5f9', color: '#475569', fontWeight: 600 }}>
                TF-IDF + Cosine Similarity
              </span>
            </div>

            {/* 2-Column Responsive Grid for Related Tickets & Escalation Assessment */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px' }}>
              
              {/* Sub-Panel 1: Possible Related Tickets */}
              <div style={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 'var(--radius-sm)', padding: '16px', display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.88rem', color: '#1e293b' }}>
                    <Layers size={16} color="#3b82f6" /> Possible Related Tickets
                  </div>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>
                    {relatedLoading ? 'Scanning...' : `${relatedTickets.length} found`}
                  </span>
                </div>

                {relatedLoading ? (
                  <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Scanning candidate tickets...
                  </div>
                ) : relatedTickets.length === 0 ? (
                  <div style={{ padding: '24px 16px', textAlign: 'center', backgroundColor: '#ffffff', borderRadius: 'var(--radius-xs)', border: '1px dashed #cbd5e1', flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                    <p style={{ margin: 0, fontSize: '0.86rem', fontWeight: 600, color: '#64748b' }}>
                      No potentially related tickets found.
                    </p>
                    <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
                      No active or historical tickets exceeded the similarity threshold.
                    </p>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
                    {relatedTickets.map((match) => (
                      <div
                        key={match.ticket_id}
                        onClick={() => navigate(`/tickets/${match.ticket_id}`)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '10px 12px',
                          backgroundColor: '#ffffff',
                          border: '1px solid #e2e8f0',
                          borderRadius: 'var(--radius-xs)',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#3b82f6'; e.currentTarget.style.boxShadow = '0 2px 6px rgba(59,130,246,0.1)'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.boxShadow = 'none'; }}
                        title="Click to inspect related ticket"
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                          <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.78rem', fontWeight: 700, color: '#3b82f6', flexShrink: 0 }}>
                            #{match.ticket_id}
                          </span>
                          <span style={{ fontSize: '0.84rem', fontWeight: 600, color: '#1e293b', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {match.title}
                          </span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0, marginLeft: '8px' }}>
                          <span style={{
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '10px',
                            backgroundColor: '#eff6ff',
                            color: '#1d4ed8',
                            border: '1px solid #bfdbfe',
                          }}>
                            {match.similarity_percentage}%
                          </span>
                          <ExternalLink size={13} color="#94a3b8" />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Sub-Panel 2: Escalation Assessment */}
              <div style={{
                backgroundColor: escalationLoading ? '#f8fafc' : (escalation?.recommendation === 'ESCALATION RECOMMENDED' ? '#fff1f2' : (escalation?.recommendation === 'MONITOR' ? '#fffbeb' : '#f0fdf4')),
                border: `1px solid ${escalationLoading ? '#e2e8f0' : (escalation?.recommendation === 'ESCALATION RECOMMENDED' ? '#fecdd3' : (escalation?.recommendation === 'MONITOR' ? '#fde68a' : '#bbf7d0'))}`,
                borderRadius: 'var(--radius-sm)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.88rem', color: '#1e293b' }}>
                    <ShieldAlert size={16} color={escalation?.recommendation === 'ESCALATION RECOMMENDED' ? '#e11d48' : (escalation?.recommendation === 'MONITOR' ? '#d97706' : '#059669')} /> Escalation Assessment
                  </div>
                  {escalation && (
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 800,
                      padding: '2px 8px',
                      borderRadius: '12px',
                      backgroundColor: escalation.recommendation === 'ESCALATION RECOMMENDED' ? '#ffe4e6' : (escalation.recommendation === 'MONITOR' ? '#fef3c7' : '#dcfce7'),
                      color: escalation.recommendation === 'ESCALATION RECOMMENDED' ? '#be123c' : (escalation.recommendation === 'MONITOR' ? '#b45309' : '#15803d'),
                      letterSpacing: '0.02em',
                    }}>
                      Risk Score: {escalation.risk_score}
                    </span>
                  )}
                </div>

                {escalationLoading ? (
                  <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Evaluating risk indicators...
                  </div>
                ) : !escalation ? (
                  <div style={{ padding: '16px', textAlign: 'center', color: '#64748b', fontSize: '0.85rem' }}>
                    Insufficient data for escalation assessment.
                  </div>
                ) : (
                  <div>
                    {/* Main Recommendation Badge */}
                    <div style={{
                      padding: '10px 14px',
                      borderRadius: 'var(--radius-xs)',
                      backgroundColor: escalation.recommendation === 'ESCALATION RECOMMENDED' ? '#e11d48' : (escalation.recommendation === 'MONITOR' ? '#d97706' : '#16a34a'),
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '14px',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {escalation.recommendation === 'ESCALATION RECOMMENDED' ? <AlertCircle size={18} /> : (escalation.recommendation === 'MONITOR' ? <AlertTriangle size={18} /> : <CheckCircle size={18} />)}
                        <span style={{ fontWeight: 800, fontSize: '0.88rem', letterSpacing: '0.03em' }}>
                          {escalation.recommendation}
                        </span>
                      </div>
                      <span style={{ fontSize: '0.72rem', opacity: 0.9 }}>
                        {escalation.risk_score >= 5 ? 'High Urgency' : (escalation.risk_score >= 3 ? 'Review Required' : 'Standard Queue')}
                      </span>
                    </div>

                    {/* Key Metric Chips */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginBottom: '14px' }}>
                      <div style={{ backgroundColor: 'rgba(255,255,255,0.7)', padding: '6px 10px', borderRadius: '4px', fontSize: '0.78rem' }}>
                        <span style={{ color: '#64748b', display: 'block', fontSize: '0.68rem', textTransform: 'uppercase' }}>Priority</span>
                        <strong>{ticket.priority}</strong>
                      </div>
                      <div style={{ backgroundColor: 'rgba(255,255,255,0.7)', padding: '6px 10px', borderRadius: '4px', fontSize: '0.78rem' }}>
                        <span style={{ color: '#64748b', display: 'block', fontSize: '0.68rem', textTransform: 'uppercase' }}>Affected Users</span>
                        <strong>{escalation.affected_users}</strong>
                      </div>
                      <div style={{ backgroundColor: 'rgba(255,255,255,0.7)', padding: '6px 10px', borderRadius: '4px', fontSize: '0.78rem' }}>
                        <span style={{ color: '#64748b', display: 'block', fontSize: '0.68rem', textTransform: 'uppercase' }}>Related Tickets</span>
                        <strong>{escalation.related_tickets_count}</strong>
                      </div>
                      <div style={{ backgroundColor: 'rgba(255,255,255,0.7)', padding: '6px 10px', borderRadius: '4px', fontSize: '0.78rem' }}>
                        <span style={{ color: '#64748b', display: 'block', fontSize: '0.68rem', textTransform: 'uppercase' }}>SLA Status</span>
                        <strong>{escalation.sla_status}</strong>
                      </div>
                    </div>

                    {/* Reasons List */}
                    <div>
                      <span style={{ fontSize: '0.74rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.04em', display: 'block', marginBottom: '6px' }}>
                        Assessment Reasons:
                      </span>
                      <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '0.82rem', color: '#334155', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {escalation.reasons.map((r, idx) => (
                          <li key={idx} style={{ lineHeight: 1.4 }}>
                            {r.replace(/^-\s*/, '')}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>

            </div>
          </div>

          {/* Comments Discussion Section */}
          <div className="card">
            <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
              <MessageSquare size={18} /> Conversation & Updates ({comments.length})
            </h2>

            {/* Comments Thread */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
              {comments.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.88rem', fontStyle: 'italic' }}>
                  No messages posted yet. Use the form below to communicate with the IT support team.
                </div>
              ) : (
                comments.map((comment) => (
                  <div
                    key={comment.id}
                    style={{
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '14px 18px',
                      backgroundColor: comment.user_id === user.id ? '#f8fafc' : '#ffffff',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{comment.user_name}</span>
                        <span
                          style={{
                            fontSize: '0.7rem',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            backgroundColor: comment.user_role === 'ADMIN' ? '#f3e8ff' : comment.user_role === 'SUPPORT_AGENT' ? '#dbeafe' : '#f1f5f9',
                            color: comment.user_role === 'ADMIN' ? '#6b21a8' : comment.user_role === 'SUPPORT_AGENT' ? '#1e40af' : '#475569',
                            fontWeight: 600,
                          }}
                        >
                          {comment.user_role}
                        </span>
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {new Date(comment.created_at).toLocaleString()}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', whiteSpace: 'pre-wrap' }}>
                      {comment.comment}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Add Comment Box */}
            <form onSubmit={handlePostComment}>
              <div className="form-group" style={{ marginBottom: '10px' }}>
                <textarea
                  required
                  rows={3}
                  className="form-textarea"
                  placeholder="Type your reply, diagnostic log, or question here..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={commentLoading || !newComment.trim()}
                style={{ padding: '8px 18px' }}
              >
                <Send size={15} /> {commentLoading ? 'Posting...' : 'Post Message'}
              </button>
            </form>
          </div>

          {/* Chronological Status Audit Timeline */}
          <div className="card">
            <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <History size={18} /> Ticket Status History Audit Trail
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {history.map((h, i) => (
                <div
                  key={h.id || i}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                    fontSize: '0.85rem',
                    borderLeft: '2px solid var(--border-color)',
                    paddingLeft: '14px',
                    marginLeft: '8px',
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                      {h.old_status ? (
                        <>
                          <span style={{ color: '#64748b' }}>{h.old_status}</span> →{' '}
                          <span style={{ color: 'var(--primary)' }}>{h.new_status}</span>
                        </>
                      ) : (
                        <span style={{ color: 'var(--primary)' }}>Ticket Created (OPEN)</span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                      By {h.author_name} ({h.author_role}) • {new Date(h.changed_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Metadata Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* SLA Status Card */}
          <div className="card">
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
              Service Level Agreement (SLA)
            </div>
            <div style={{ marginBottom: '12px' }}>
              <SlaBadge
                slaStatus={ticket.sla_status}
                remainingHours={ticket.sla_remaining_hours}
                isBreached={ticket.is_breached}
              />
            </div>
            <div style={{ fontSize: '0.85rem', color: '#475569' }}>
              <strong>Due Target:</strong>{' '}
              {ticket.due_at ? new Date(ticket.due_at).toLocaleString() : 'N/A'}
            </div>
          </div>

          {/* Ticket Attributes */}
          <div className="card">
            <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              Ticket Attributes
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '0.88rem' }}>
              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Category</span>
                <span style={{ fontWeight: 600 }}>{ticket.category_name || 'N/A'}</span>
              </div>

              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Reported By</span>
                <span style={{ fontWeight: 600 }}>{ticket.creator_name}</span>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>{ticket.creator_email}</span>
              </div>

              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Assigned Agent</span>
                <span style={{ fontWeight: 600 }}>{ticket.assignee_name || 'Unassigned'}</span>
                {ticket.assignee_email && (
                  <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>{ticket.assignee_email}</span>
                )}
              </div>

              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Submitted On</span>
                <span>{new Date(ticket.created_at).toLocaleString()}</span>
              </div>

              <div>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Last Activity</span>
                <span>{new Date(ticket.updated_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal: Assign Ticket */}
      <Modal
        isOpen={isAssignOpen}
        onClose={() => setIsAssignOpen(false)}
        title="Assign Ticket to Support Agent"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsAssignOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleAssign} disabled={actionLoading || !selectedAgent}>
              {actionLoading ? 'Assigning...' : 'Confirm Assignment'}
            </button>
          </>
        }
      >
        <div className="form-group">
          <label className="form-label">Select Support Agent or Administrator</label>
          <select
            className="form-select"
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
          >
            <option value="">-- Choose Agent --</option>
            {agents.map((ag) => (
              <option key={ag.id} value={ag.id}>
                {ag.name} ({ag.email}) - {ag.role}
              </option>
            ))}
          </select>
        </div>
      </Modal>

      {/* Modal: Update Status */}
      <Modal
        isOpen={isStatusOpen}
        onClose={() => setIsStatusOpen(false)}
        title="Transition Ticket Status"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsStatusOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleUpdateStatus} disabled={actionLoading || !nextStatus}>
              {actionLoading ? 'Updating...' : 'Update Status'}
            </button>
          </>
        }
      >
        <div className="form-group">
          <label className="form-label">Select Next Status</label>
          <select
            className="form-select"
            value={nextStatus}
            onChange={(e) => setNextStatus(e.target.value)}
          >
            <option value="ASSIGNED">ASSIGNED (Agent accepted)</option>
            <option value="IN_PROGRESS">IN_PROGRESS (Under investigation)</option>
          </select>
        </div>
      </Modal>

      {/* Modal: Resolve Ticket */}
      <Modal
        isOpen={isResolveOpen}
        onClose={() => setIsResolveOpen(false)}
        title="Resolve Ticket"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsResolveOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-success" onClick={handleResolve} disabled={actionLoading || !resolutionNotes.trim()}>
              {actionLoading ? 'Resolving...' : 'Complete Resolution'}
            </button>
          </>
        }
      >
        <div className="form-group">
          <label className="form-label">Resolution Notes / Action Taken *</label>
          <textarea
            required
            rows={5}
            className="form-textarea"
            placeholder="Explain the root cause and specific remedy applied (e.g. replaced SSD cable, flushed DNS, patched driver)..."
            value={resolutionNotes}
            onChange={(e) => setResolutionNotes(e.target.value)}
          />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            These notes will be archived and presented to the employee for verification.
          </span>
        </div>
      </Modal>

      {/* Modal: Reopen Ticket */}
      <Modal
        isOpen={isReopenOpen}
        onClose={() => setIsReopenOpen(false)}
        title="Reopen Service Ticket"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsReopenOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleReopen} disabled={actionLoading || !reopenReason.trim()}>
              {actionLoading ? 'Reopening...' : 'Reopen Ticket'}
            </button>
          </>
        }
      >
        <div className="form-group">
          <label className="form-label">Why is the issue not resolved? *</label>
          <textarea
            required
            rows={4}
            className="form-textarea"
            placeholder="Describe what error is still occurring or why the fix did not work..."
            value={reopenReason}
            onChange={(e) => setReopenReason(e.target.value)}
          />
        </div>
      </Modal>

      {/* Confirm Dialog: Delete Ticket */}
      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDelete}
        title="Delete Ticket"
        message={`Are you sure you want to permanently delete Ticket #${ticket.id}? This will remove all associated comments, status changes, and history.`}
        confirmText="Delete Ticket"
        isDestructive={true}
        loading={actionLoading}
      />
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ticketService } from '../services/ticketService';
import { categoryService } from '../services/categoryService';
import { PriorityBadge } from '../components/PriorityBadge';
import { PriorityRecommenderModal } from '../components/PriorityRecommenderModal';
import { ErrorMessage } from '../components/ErrorMessage';
import { Sparkles, ArrowLeft, Send } from 'lucide-react';

export const CreateTicket = () => {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [priority, setPriority] = useState('MEDIUM');

  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isAdvisorOpen, setIsAdvisorOpen] = useState(false);

  useEffect(() => {
    categoryService.listCategories(true)
      .then((data) => {
        setCategories(data || []);
        if (data && data.length > 0) {
          setCategoryId(data[0].id);
        }
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch categories');
      })
      .finally(() => {
        setCategoriesLoading(false);
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!categoryId) {
      setError('Please select an issue category');
      return;
    }

    setLoading(true);
    try {
      const created = await ticketService.createTicket({
        title,
        description,
        category_id: Number(categoryId),
        priority,
      });
      navigate(`/tickets/${created.id}`);
    } catch (err) {
      setError(err.message || 'Failed to create ticket');
    } finally {
      setLoading(false);
    }
  };

  const getSelectedCategoryName = () => {
    const found = categories.find((c) => c.id === Number(categoryId));
    return found ? found.name : '';
  };

  return (
    <div className="page-body" style={{ maxWidth: '800px' }}>
      <button
        className="btn btn-sm btn-secondary"
        onClick={() => navigate(-1)}
        style={{ marginBottom: '18px' }}
      >
        <ArrowLeft size={16} /> Back
      </button>

      <div className="card">
        <div style={{ marginBottom: '24px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Raise an IT Service Ticket
          </h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Provide technical details to help our IT support team triage and resolve your problem quickly.
          </p>
        </div>

        {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Issue Summary / Title *</label>
            <input
              type="text"
              required
              minLength={5}
              maxLength={200}
              className="form-input"
              placeholder="e.g. Cannot connect to Office VPN from macOS Sequoia"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Concise summary of the problem (minimum 5 characters)
            </span>
          </div>

          <div className="form-row-2">
            <div className="form-group">
              <label className="form-label">Category *</label>
              <select
                className="form-select"
                required
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
                disabled={categoriesLoading}
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label className="form-label" style={{ marginBottom: 0 }}>Priority Level *</label>
                <button
                  type="button"
                  onClick={() => setIsAdvisorOpen(true)}
                  style={{
                    fontSize: '0.78rem',
                    color: 'var(--primary)',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '2px 6px',
                    borderRadius: 'var(--radius-xs)',
                    backgroundColor: 'var(--primary-light)',
                  }}
                >
                  <Sparkles size={13} /> Smart Advisor
                </button>
              </div>

              <select
                className="form-select"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                <option value="LOW">LOW (72h SLA - Minor / Non-blocking)</option>
                <option value="MEDIUM">MEDIUM (48h SLA - General issue)</option>
                <option value="HIGH">HIGH (24h SLA - Significant impact)</option>
                <option value="CRITICAL">CRITICAL (4h SLA - Outage / Security)</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Detailed Description *</label>
            <textarea
              required
              minLength={10}
              rows={6}
              className="form-textarea"
              placeholder="Please describe what happened, steps to reproduce, error codes, and device details..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Include relevant details like application version, OS, or specific error text.
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/tickets')}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ minWidth: '150px' }}
            >
              <Send size={16} /> {loading ? 'Submitting...' : 'Submit Ticket'}
            </button>
          </div>
        </form>
      </div>

      <PriorityRecommenderModal
        isOpen={isAdvisorOpen}
        onClose={() => setIsAdvisorOpen(false)}
        onSelectPriority={(recommendedPriority) => setPriority(recommendedPriority)}
        defaultCategory={getSelectedCategoryName()}
      />
    </div>
  );
};

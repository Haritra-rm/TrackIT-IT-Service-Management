import React, { useState, useEffect } from 'react';
import { categoryService } from '../services/categoryService';
import { Modal } from '../components/Modal';
import { ErrorMessage } from '../components/ErrorMessage';
import { FolderKanban, PlusCircle, Edit3, CheckCircle, XCircle } from 'lucide-react';

export const CategoriesManagement = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal create/edit state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [form, setForm] = useState({ name: '', description: '', is_active: true });
  const [actionLoading, setActionLoading] = useState(false);

  const fetchCategories = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await categoryService.listCategories(false);
      setCategories(data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch categories');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleOpenCreate = () => {
    setEditingCategory(null);
    setForm({ name: '', description: '', is_active: true });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (cat) => {
    setEditingCategory(cat);
    setForm({ name: cat.name, description: cat.description || '', is_active: cat.is_active });
    setIsModalOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      if (editingCategory) {
        await categoryService.updateCategory(editingCategory.id, form);
      } else {
        await categoryService.createCategory(form);
      }
      setIsModalOpen(false);
      fetchCategories();
    } catch (err) {
      setError(err.message || 'Failed to save category');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="page-body">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
            Ticket Issue Categories
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
            Configure organization ticket classifications used in SLA routing and reports.
          </p>
        </div>

        <button className="btn btn-primary" onClick={handleOpenCreate}>
          <PlusCircle size={16} /> New Category
        </button>
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      <div className="card" style={{ padding: 0 }}>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Category Name</th>
                <th>Description</th>
                <th>Status</th>
                <th>Total Tickets</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((cat) => (
                <tr key={cat.id}>
                  <td>
                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{cat.name}</span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '350px' }}>
                    {cat.description || 'No description provided'}
                  </td>
                  <td>
                    {cat.is_active ? (
                      <span className="badge" style={{ backgroundColor: 'var(--success-light)', color: 'var(--success-text)', border: '1px solid var(--success-border)' }}>
                        <CheckCircle size={11} strokeWidth={2.5} /> Active
                      </span>
                    ) : (
                      <span className="badge" style={{ backgroundColor: 'var(--slate-100)', color: 'var(--slate-600)', border: '1px solid var(--slate-300)' }}>
                        <XCircle size={11} strokeWidth={2.5} /> Inactive
                      </span>
                    )}
                  </td>
                  <td>
                    <span style={{ fontWeight: 600 }}>{cat.ticket_count ?? 0}</span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      className="btn btn-sm btn-secondary"
                      onClick={() => handleOpenEdit(cat)}
                      style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                    >
                      <Edit3 size={13} /> Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingCategory ? 'Edit Issue Category' : 'Create Issue Category'}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleSave} disabled={actionLoading}>
              {actionLoading ? 'Saving...' : 'Save Category'}
            </button>
          </>
        }
      >
        <form onSubmit={handleSave}>
          <div className="form-group">
            <label className="form-label">Category Name *</label>
            <input
              type="text"
              required
              className="form-input"
              placeholder="e.g. Cloud Infrastructure"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              rows={3}
              className="form-textarea"
              placeholder="Define what issues fall under this classification..."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px' }}>
            <input
              type="checkbox"
              id="is_active_toggle"
              checked={form.is_active}
              onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
            />
            <label htmlFor="is_active_toggle" style={{ fontSize: '0.88rem', cursor: 'pointer' }}>
              Category is active for new ticket submission
            </label>
          </div>
        </form>
      </Modal>
    </div>
  );
};

import { api } from './api';

export const ticketService = {
  listTickets: (params = {}) => {
    return api.get('/tickets', params);
  },

  getTicket: (id) => {
    return api.get(`/tickets/${id}`);
  },

  createTicket: (payload) => {
    return api.post('/tickets', payload);
  },

  updateTicket: (id, payload) => {
    return api.put(`/tickets/${id}`, payload);
  },

  deleteTicket: (id) => {
    return api.delete(`/tickets/${id}`);
  },

  assignTicket: (id, assignedTo) => {
    return api.post(`/tickets/${id}/assign`, { assigned_to: assignedTo });
  },

  updateStatus: (id, status, notes = '') => {
    return api.post(`/tickets/${id}/status`, { status, notes });
  },

  resolveTicket: (id, resolutionNotes) => {
    return api.post(`/tickets/${id}/resolve`, { resolution_notes: resolutionNotes });
  },

  reopenTicket: (id, reason) => {
    return api.post(`/tickets/${id}/reopen`, { reason });
  },

  getComments: (id) => {
    return api.get(`/tickets/${id}/comments`);
  },

  addComment: (id, comment) => {
    return api.post(`/tickets/${id}/comments`, { comment });
  },

  getHistory: (id) => {
    return api.get(`/tickets/${id}/history`);
  },

  recommendPriority: (payload) => {
    return api.post('/tickets/recommend-priority', payload);
  },
};

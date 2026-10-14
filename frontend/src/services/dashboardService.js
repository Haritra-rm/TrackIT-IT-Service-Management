import { api } from './api';

export const dashboardService = {
  getSummary: () => {
    return api.get('/dashboard/summary');
  },

  getTicketsByStatus: () => {
    return api.get('/dashboard/tickets-by-status');
  },

  getTicketsByPriority: () => {
    return api.get('/dashboard/tickets-by-priority');
  },

  getTicketsByCategory: () => {
    return api.get('/dashboard/tickets-by-category');
  },

  getAgentPerformance: () => {
    return api.get('/dashboard/agent-performance');
  },

  getAuditLogs: (limit = 50, entityType = null) => {
    return api.get('/audit-logs', { limit, entity_type: entityType });
  },
};

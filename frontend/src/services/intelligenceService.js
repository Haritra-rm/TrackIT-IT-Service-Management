import { api } from './api';

export const intelligenceService = {
  getRelatedTickets: (ticketId, threshold = 0.5) => {
    return api.get(`/intelligence/tickets/${ticketId}/related`, { threshold });
  },

  getEscalationAssessment: (ticketId, threshold = 0.5) => {
    return api.get(`/intelligence/tickets/${ticketId}/escalation`, { threshold });
  },
};

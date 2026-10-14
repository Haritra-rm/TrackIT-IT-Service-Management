import { api } from './api';

export const userService = {
  listUsers: (params = {}) => {
    return api.get('/users', params);
  },

  getAgents: () => {
    return api.get('/users/agents');
  },

  getUser: (id) => {
    return api.get(`/users/${id}`);
  },

  updateUser: (id, payload) => {
    return api.put(`/users/${id}`, payload);
  },

  updateStatus: (id, isActive) => {
    return api.patch(`/users/${id}/status`, { is_active: isActive });
  },
};

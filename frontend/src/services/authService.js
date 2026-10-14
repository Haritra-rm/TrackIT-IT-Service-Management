import { api } from './api';

export const authService = {
  login: async (email, password) => {
    const data = await api.post('/auth/login', { email, password });
    if (data.access_token) {
      localStorage.setItem('trackit_token', data.access_token);
      localStorage.setItem('trackit_user', JSON.stringify(data.user));
    }
    return data;
  },

  register: async (payload) => {
    return api.post('/auth/register', payload);
  },

  getMe: async () => {
    return api.get('/auth/me');
  },

  logout: () => {
    localStorage.removeItem('trackit_token');
    localStorage.removeItem('trackit_user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('trackit_user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  getToken: () => {
    return localStorage.getItem('trackit_token');
  },
};

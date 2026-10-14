import { api } from './api';

export const categoryService = {
  listCategories: (activeOnly = false) => {
    return api.get('/categories', { active_only: activeOnly });
  },

  createCategory: (payload) => {
    return api.post('/categories', payload);
  },

  updateCategory: (id, payload) => {
    return api.put(`/categories/${id}`, payload);
  },
};

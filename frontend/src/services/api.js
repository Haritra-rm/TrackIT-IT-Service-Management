const API_BASE = '/api/v1';

export class ApiError extends Error {
  constructor(message, code = 'ERROR', status = 400, details = null) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const token = localStorage.getItem('trackit_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    // 204 No Content
    if (response.status === 204) {
      return null;
    }

    const json = await response.json().catch(() => null);

    if (!response.ok) {
      const code = json?.error?.code || 'HTTP_ERROR';
      const message = json?.error?.message || response.statusText || 'Request failed';
      const details = json?.error?.details || null;

      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        // Token expired or invalid
        localStorage.removeItem('trackit_token');
        localStorage.removeItem('trackit_user');
        window.dispatchEvent(new Event('trackit_logout'));
      }

      throw new ApiError(message, code, response.status, details);
    }

    return json?.data !== undefined ? json.data : json;
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(err.message || 'Network connection error', 'NETWORK_ERROR', 0);
  }
}

export const api = {
  get: (endpoint, params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, val);
      }
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request(`${endpoint}${qs}`, { method: 'GET' });
  },

  post: (endpoint, body = {}) => {
    return request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  put: (endpoint, body = {}) => {
    return request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  },

  patch: (endpoint, body = {}) => {
    return request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body),
    });
  },

  delete: (endpoint) => {
    return request(endpoint, { method: 'DELETE' });
  },
};

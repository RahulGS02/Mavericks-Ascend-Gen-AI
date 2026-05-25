/**
 * API client with authentication interceptor
 */
import axios, { AxiosError, AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// API endpoints
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (data: { email: string; password: string; name: string; role: string }) =>
    api.post('/auth/register', data),

  getCurrentUser: () =>
    api.get('/auth/me'),

  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    }),

  logout: () =>
    api.post('/auth/logout'),
};

// Natural Language Query API (Super Admin)
export const nlQueryAPI = {
  search: (query: string, maxRows: number = 100) =>
    api.post('/nl-query/search', { query, max_rows: maxRows }),

  downloadExcel: (query: string, maxRows: number = 100) =>
    api.post('/nl-query/search/download',
      { query, max_rows: maxRows },
      { responseType: 'blob' }
    ),
};

// AI-Powered Talent Search API (HR, Manager, Super Admin)
export const talentSearchAPI = {
  // Main search endpoint
  search: (params: {
    query: string;
    max_results?: number;
    include_similar?: boolean;
    urgency?: 'immediate' | 'flexible';
  }) =>
    api.post('/talent-search/search', params),

  // Explain why a candidate was suggested
  explain: (candidateId: string, requiredSkills: string[]) =>
    api.get(`/talent-search/explain/${candidateId}`, {
      params: { required_skills: requiredSkills.join(',') }
    }),

  // Get cost estimate for AI search
  getCostEstimate: () =>
    api.get('/talent-search/cost-estimate'),

  // Get talent pool statistics
  getStatistics: () =>
    api.get('/talent-search/statistics'),
};

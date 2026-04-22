/**
 * API client with authentication interceptor
 */
import axios, { AxiosError, AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
    api.post('/api/v1/auth/login', { email, password }),
  
  register: (data: { email: string; password: string; name: string; role: string }) =>
    api.post('/api/v1/auth/register', data),
  
  getCurrentUser: () =>
    api.get('/api/v1/auth/me'),
  
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    }),
  
  logout: () =>
    api.post('/api/v1/auth/logout'),
};

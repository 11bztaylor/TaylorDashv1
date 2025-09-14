import axios from 'axios';
import { ApiResponse, HealthResponse, Project } from '../types/api';

// Prefer explicit origin for remote access, fall back to current origin
const API_ORIGIN = import.meta.env.VITE_API_ORIGIN || window.location.origin;

const api = axios.create({
  baseURL: `${API_ORIGIN}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    // For dev: allow API key header if present. For prod, prefer session token only.
    ...(import.meta.env.VITE_API_KEY ? { 'X-API-Key': import.meta.env.VITE_API_KEY } : {}),
  },
});

// Attach Bearer token (if present) and optional debug logging
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('taylordash_session_token');
    if (token) {
      config.headers = {
        ...(config.headers || {}),
        Authorization: `Bearer ${token}`,
      };
    }
    if (import.meta.env.MODE === 'development') {
      // eslint-disable-next-line no-console
      console.log('API Request:', config.method?.toUpperCase(), config.url);
    }
    return config;
  },
  (error) => {
    if (import.meta.env.MODE === 'development') {
      // eslint-disable-next-line no-console
      console.error('API Request Error:', error);
    }
    return Promise.reject(error);
  }
);

// Optional response logging in dev
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.MODE === 'development') {
      // eslint-disable-next-line no-console
      console.log('API Response:', response.status, response.config.url);
    }
    return response;
  },
  (error) => {
    if (import.meta.env.MODE === 'development') {
      // eslint-disable-next-line no-console
      console.error('API Response Error:', error.response?.status, error.response?.data);
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/v1/health/stack');
    return response.data;
  },

  // Projects
  async getProjects(): Promise<Project[]> {
    const response = await api.get<any>('/v1/projects');
    return response.data.projects;
  },

  async getProject(id: string): Promise<Project> {
    const response = await api.get<ApiResponse<Project>>(`/v1/projects/${id}`);
    return response.data.data;
  },

  async createProject(project: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<Project> {
    const response = await api.post<ApiResponse<Project>>('/v1/projects', project);
    return response.data.data;
  },

  async updateProject(id: string, project: Partial<Project>): Promise<Project> {
    const response = await api.put<ApiResponse<Project>>(`/v1/projects/${id}`, project);
    return response.data.data;
  },

  async deleteProject(id: string): Promise<void> {
    await api.delete(`/v1/projects/${id}`);
  },
};

export default api;

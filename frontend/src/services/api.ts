import axios from 'axios';
import { ApiResponse, HealthResponse, Project } from '../types/api';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': import.meta.env.VITE_API_KEY,
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data);
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
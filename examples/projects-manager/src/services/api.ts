import axios from 'axios';

// Create axios instance with API key authentication
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'taylordash-dev-key', // Use the API key from security implementation
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response ${response.status}:`, response.data);
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error);
    if (error.response?.status === 401) {
      console.error('[API] Authentication failed - check API key');
    }
    return Promise.reject(error);
  }
);

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed';
  owner_id: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed';
  owner_id: string;
  metadata: Record<string, any>;
}

export interface ProjectsResponse {
  projects: Project[];
  count: number;
}

// Projects API
export const projectsApi = {
  // Get all projects
  getAll: async (): Promise<ProjectsResponse> => {
    const response = await api.get<ProjectsResponse>('/v1/projects');
    return response.data;
  },

  // Get project by ID
  getById: async (id: string): Promise<Project> => {
    const response = await api.get<Project>(`/v1/projects/${id}`);
    return response.data;
  },

  // Create new project
  create: async (project: ProjectCreate): Promise<Project> => {
    const response = await api.post<Project>('/v1/projects', project);
    return response.data;
  },

  // Update project
  update: async (id: string, updates: Partial<ProjectCreate>): Promise<Project> => {
    const response = await api.put<Project>(`/v1/projects/${id}`, updates);
    return response.data;
  },

  // Delete project
  delete: async (id: string): Promise<void> => {
    await api.delete(`/v1/projects/${id}`);
  },
};

export default api;
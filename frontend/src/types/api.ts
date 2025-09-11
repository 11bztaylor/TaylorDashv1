export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'completed';
  owner_id?: string;
  metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface HealthResponse {
  overall_status: string;
  services: {
    [key: string]: {
      status: string;
      type: string;
      message: string;
    };
  };
  timestamp: string;
}
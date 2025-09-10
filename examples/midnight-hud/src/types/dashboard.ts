export interface Widget {
  id: string;
  type: 'system' | 'project' | 'metrics' | 'alerts';
  title: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  isMinimized: boolean;
  isPinned: boolean;
  zIndex: number;
}

export interface DashboardState {
  widgets: Widget[];
  activeView: 'home' | 'library';
}

export interface SystemData {
  cpu: number;
  memory: number;
  disk: number;
  network: { up: number; down: number };
  uptime: string;
}

export interface ProjectData {
  name: string;
  status: 'running' | 'idle' | 'error';
  progress: number;
  lastUpdate: string;
}

export interface MetricsData {
  requests: number;
  errors: number;
  latency: number;
  throughput: number;
}

export interface AlertData {
  id: string;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
}
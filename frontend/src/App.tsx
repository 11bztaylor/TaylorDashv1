import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Folder, Settings, Layers, Plug } from 'lucide-react';
import { ErrorBoundary, NotificationContainer, AsyncErrorBoundary } from './components/ErrorBoundary';
import { PluginPage } from './components/PluginPage';
import { apiCall, notificationManager, measureAsyncPerformance } from './utils/errorHandling';
import { eventBusService } from './services/eventBus';

// Simple inline components to avoid import issues
const ConnectionStatus: React.FC<{ onConnectionChange: (connected: boolean) => void }> = ({ onConnectionChange }) => {
  const [isConnected, setIsConnected] = useState(false);
  
  React.useEffect(() => {
    // Simulate connection check
    const checkConnection = async () => {
      try {
        const response = await fetch('/api/v1/health/stack', {
          headers: {
            'X-API-Key': import.meta.env.VITE_API_KEY || 'taylordash-dev-key'
          }
        });
        const connected = response.ok;
        setIsConnected(connected);
        onConnectionChange(connected);
      } catch (error) {
        setIsConnected(false);
        onConnectionChange(false);
      }
    };
    
    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [onConnectionChange]);

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
      <span className="text-sm text-gray-400">
        {isConnected ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  );
};

const ProjectsList: React.FC<{ onProjectsChange?: () => void }> = ({ onProjectsChange }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/projects', {
        headers: {
          'X-API-Key': import.meta.env.VITE_API_KEY || 'taylordash-dev-key'
        }
      });
      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects || []);
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchProjects();
  }, []);

  React.useEffect(() => {
    if (onProjectsChange) {
      fetchProjects();
    }
  }, [onProjectsChange]);

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Projects</h2>
      {loading ? (
        <p className="text-gray-400 text-sm">Loading projects...</p>
      ) : (
        <div>
          <p className="text-gray-400 text-sm mb-4">
            {projects.length === 0 ? 'No projects yet. Start by creating your first project!' : `${projects.length} projects`}
          </p>
          {projects.length > 0 && (
            <div className="space-y-3">
              {projects.map((project: any) => (
                <div key={project.id} className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-white font-medium">{project.name}</h3>
                  <p className="text-gray-300 text-sm mt-1">{project.description}</p>
                  <div className="flex items-center mt-2 space-x-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      project.status === 'active' ? 'bg-green-900 text-green-300' :
                      project.status === 'completed' ? 'bg-blue-900 text-blue-300' :
                      'bg-gray-600 text-gray-300'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const FlowCanvas: React.FC = () => {
  return (
    <div className="bg-gray-800 rounded-lg p-6 h-64">
      <h2 className="text-xl font-semibold text-white mb-4">System Flow</h2>
      <div className="flex items-center justify-center h-full bg-gray-700 rounded">
        <p className="text-gray-400">Visual flow canvas coming soon...</p>
      </div>
    </div>
  );
};

// Layout wrapper component
const Layout: React.FC<{ children: React.ReactNode; title: string }> = ({ children, title }) => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<string>('');

  React.useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString());
    };
    
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">TaylorDash</h1>
            <span className="text-sm text-gray-400">{title}</span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-300 font-mono">
              {currentTime}
            </div>
            <ConnectionStatus onConnectionChange={setIsConnected} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {children}
      </main>

      {/* Status Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 px-6 py-2">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center space-x-4">
            <span>Backend Status: {isConnected ? 'Connected' : 'Disconnected'}</span>
            <span>•</span>
            <span>API Endpoint: /api</span>
            <span>•</span>
            <span>Version: 1.0.0</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span>System Health</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  return (
    <Layout title="Dashboard">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-16">
        {/* Projects Section */}
        <div className="space-y-6">
          <ProjectsList />
        </div>

        {/* Canvas Section */}
        <div className="space-y-6">
          <FlowCanvas />
        </div>
      </div>
    </Layout>
  );
};

// Project Creation Modal Component
const ProjectCreateModal: React.FC<{ isOpen: boolean; onClose: () => void; onSuccess: () => void }> = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    status: 'planning',
    owner_id: '00000000-0000-0000-0000-000000000001' // Default UUID for now
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setError('Project name is required');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': import.meta.env.VITE_API_KEY || 'taylordash-dev-key',
        },
        body: JSON.stringify({
          ...formData,
          metadata: {}
        }),
      });

      if (response.ok) {
        setFormData({ name: '', description: '', status: 'planning', owner_id: '00000000-0000-0000-0000-000000000001' });
        onSuccess();
        onClose();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create project');
      }
    } catch (error) {
      setError('Network error occurred');
      console.error('Error creating project:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">Create New Project</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
            disabled={loading}
          >
            ×
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Project Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                placeholder="Enter project name"
                disabled={loading}
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                placeholder="Enter project description"
                rows={3}
                disabled={loading}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
                disabled={loading}
              >
                <option value="planning">Planning</option>
                <option value="active">Active</option>
                <option value="on_hold">On Hold</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
          
          {error && (
            <div className="mt-4 p-3 bg-red-900 border border-red-700 rounded text-red-300 text-sm">
              {error}
            </div>
          )}
          
          <div className="flex space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const ProjectsPage: React.FC = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [projectsRefreshTrigger, setProjectsRefreshTrigger] = useState(0);

  const handleProjectCreated = () => {
    setProjectsRefreshTrigger(prev => prev + 1);
  };

  return (
    <Layout title="Project Management">
      <div className="pb-16">
        <div className="mb-6">
          <button 
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            + New Project
          </button>
        </div>
        <ProjectsList 
          key={projectsRefreshTrigger}
          onProjectsChange={projectsRefreshTrigger > 0 ? () => {} : undefined}
        />
      </div>
      <ProjectCreateModal 
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleProjectCreated}
      />
    </Layout>
  );
};

const FlowPage: React.FC = () => {
  return (
    <Layout title="Flow Canvas">
      <div className="pb-16 h-screen">
        <FlowCanvas />
      </div>
    </Layout>
  );
};

// Log viewer interfaces
interface LogEntry {
  id: number;
  timestamp: string;
  level: string;
  service: string;
  category: string;
  severity: string;
  message: string;
  details?: string;
  trace_id?: string;
  endpoint?: string;
  method?: string;
  error_code?: string;
  context?: any;
}

interface LogFilters {
  level: string;
  service: string;
  category: string;
  search: string;
}

const LogViewer: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<LogFilters>({
    level: 'ALL',
    service: 'ALL',
    category: 'ALL',
    search: ''
  });
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);

  // Fetch logs from backend
  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.level !== 'ALL') params.append('level', filters.level);
      if (filters.service !== 'ALL') params.append('service', filters.service);
      if (filters.category !== 'ALL') params.append('category', filters.category);
      if (filters.search) params.append('search', filters.search);
      params.append('limit', '100');

      const data = await measureAsyncPerformance(
        () => apiCall(`/logs?${params.toString()}`),
        'fetchLogs',
        2000 // 2 second threshold
      );
      
      setLogs(data.logs || []);
      
      if (data.logs && data.logs.length > 0) {
        notificationManager.showSuccess(
          `Loaded ${data.logs.length} log entries`,
          'Logs Updated'
        );
      }
    } catch (error) {
      notificationManager.showError(error as any);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh effect
  React.useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchLogs, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, filters]);

  // Initial fetch
  React.useEffect(() => {
    fetchLogs();
  }, [filters]);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR': return 'text-red-400 bg-red-900/20';
      case 'WARN': return 'text-yellow-400 bg-yellow-900/20';
      case 'INFO': return 'text-blue-400 bg-blue-900/20';
      case 'DEBUG': return 'text-gray-400 bg-gray-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'text-red-300 bg-red-900/30';
      case 'HIGH': return 'text-orange-300 bg-orange-900/30';
      case 'MEDIUM': return 'text-yellow-300 bg-yellow-900/30';
      case 'LOW': return 'text-green-300 bg-green-900/30';
      default: return 'text-gray-300 bg-gray-900/30';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">System Logs</h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              autoRefresh 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
            }`}
          >
            {autoRefresh ? 'Live' : 'Manual'}
          </button>
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Level</label>
          <select
            value={filters.level}
            onChange={(e) => setFilters(prev => ({ ...prev, level: e.target.value }))}
            className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          >
            <option value="ALL">All Levels</option>
            <option value="ERROR">Error</option>
            <option value="WARN">Warning</option>
            <option value="INFO">Info</option>
            <option value="DEBUG">Debug</option>
          </select>
        </div>
        
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Service</label>
          <select
            value={filters.service}
            onChange={(e) => setFilters(prev => ({ ...prev, service: e.target.value }))}
            className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          >
            <option value="ALL">All Services</option>
            <option value="taylordash-backend">Backend</option>
            <option value="taylordash-mqtt">MQTT</option>
            <option value="taylordash-frontend">Frontend</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Category</label>
          <select
            value={filters.category}
            onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
            className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          >
            <option value="ALL">All Categories</option>
            <option value="API">API</option>
            <option value="DATABASE">Database</option>
            <option value="MQTT">MQTT</option>
            <option value="SYSTEM">System</option>
            <option value="VALIDATION">Validation</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Search</label>
          <input
            type="text"
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            placeholder="Search logs..."
            className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm placeholder-gray-500"
          />
        </div>
      </div>

      {/* Log entries */}
      <div className="bg-gray-900 rounded-lg max-h-96 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-center text-gray-400">Loading logs...</div>
        ) : logs.length === 0 ? (
          <div className="p-4 text-center text-gray-400">No logs found</div>
        ) : (
          <div className="space-y-1">
            {logs.map((log) => (
              <div
                key={log.id}
                onClick={() => setSelectedLog(log)}
                className="p-3 hover:bg-gray-800 cursor-pointer border-b border-gray-700 last:border-b-0"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getLevelColor(log.level)}`}>
                      {log.level}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(log.severity)}`}>
                      {log.severity}
                    </span>
                    <span className="text-xs text-gray-400">{log.service}</span>
                    <span className="text-xs text-gray-500">{log.category}</span>
                  </div>
                  <span className="text-xs text-gray-500 whitespace-nowrap ml-2">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="mt-1">
                  <p className="text-sm text-white truncate">{log.message}</p>
                  {log.endpoint && (
                    <p className="text-xs text-gray-400 mt-1">
                      {log.method} {log.endpoint}
                      {log.error_code && <span className="ml-2 text-red-400">[{log.error_code}]</span>}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Log detail modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-white">Log Details</h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-gray-400 hover:text-white"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Timestamp</label>
                  <p className="text-sm text-white">{new Date(selectedLog.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Trace ID</label>
                  <p className="text-sm text-white font-mono">{selectedLog.trace_id || 'N/A'}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Level</label>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getLevelColor(selectedLog.level)}`}>
                    {selectedLog.level}
                  </span>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Service</label>
                  <p className="text-sm text-white">{selectedLog.service}</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Category</label>
                  <p className="text-sm text-white">{selectedLog.category}</p>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1">Message</label>
                <p className="text-sm text-white bg-gray-900 p-3 rounded">{selectedLog.message}</p>
              </div>

              {selectedLog.details && (
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Details</label>
                  <p className="text-sm text-white bg-gray-900 p-3 rounded whitespace-pre-wrap">{selectedLog.details}</p>
                </div>
              )}

              {selectedLog.context && (
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Context</label>
                  <pre className="text-xs text-white bg-gray-900 p-3 rounded overflow-x-auto">
                    {JSON.stringify(selectedLog.context, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('settings');

  return (
    <Layout title="Settings">
      <div className="pb-16">
        {/* Tab navigation */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('settings')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'settings'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              System Settings
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'logs'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              System Logs
            </button>
          </div>
        </div>

        {/* Tab content */}
        {activeTab === 'settings' ? (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">System Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  API Endpoint
                </label>
                <input 
                  type="text" 
                  defaultValue="/api" 
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  readOnly
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Theme
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                  <option>Dark</option>
                  <option>Light</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Auto-refresh Interval
                </label>
                <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white">
                  <option value="5">5 seconds</option>
                  <option value="10">10 seconds</option>
                  <option value="30">30 seconds</option>
                  <option value="60">1 minute</option>
                </select>
              </div>
            </div>
          </div>
        ) : (
          <LogViewer />
        )}
      </div>
    </Layout>
  );
};

const Navigation: React.FC = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/projects', icon: Folder, label: 'Projects' },
    { path: '/flow', icon: Layers, label: 'Flow Canvas' },
    { path: '/plugins/projects-manager', icon: Plug, label: 'Plugins' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <nav className="bg-gray-800 border-b border-gray-700 px-6 py-2">
      <div className="flex space-x-6">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

const App: React.FC = () => {
  // Initialize event bus service on app startup
  React.useEffect(() => {
    console.log('[App] Initializing event bus service...');
    // Event bus is initialized on import, just log for debugging
    const stats = eventBusService.getStats();
    console.log('[App] Event bus initialized with stats:', stats);
  }, []);

  return (
    <ErrorBoundary component="App">
      <AsyncErrorBoundary>
        <Router>
          <div className="min-h-screen bg-gray-900">
            <ErrorBoundary component="Navigation">
              <Navigation />
            </ErrorBoundary>
            
            <Routes>
              <Route path="/" element={
                <ErrorBoundary component="Dashboard">
                  <Dashboard />
                </ErrorBoundary>
              } />
              <Route path="/projects" element={
                <ErrorBoundary component="ProjectsPage">
                  <ProjectsPage />
                </ErrorBoundary>
              } />
              <Route path="/flow" element={
                <ErrorBoundary component="FlowPage">
                  <FlowPage />
                </ErrorBoundary>
              } />
              <Route path="/settings" element={
                <ErrorBoundary component="SettingsPage">
                  <SettingsPage />
                </ErrorBoundary>
              } />
              <Route path="/plugins/:pluginId" element={
                <ErrorBoundary component="PluginPage">
                  <PluginPage />
                </ErrorBoundary>
              } />
            </Routes>
            
            <NotificationContainer />
          </div>
        </Router>
      </AsyncErrorBoundary>
    </ErrorBoundary>
  );
};

export default App;
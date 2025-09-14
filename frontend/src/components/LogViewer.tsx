import React, { useState } from 'react';
import { notificationManager, measureAsyncPerformance } from '../utils/errorHandling';

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

export const LogViewer: React.FC = () => {
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

      const sessionToken = localStorage.getItem('taylordash_session_token');
      const headers: HeadersInit = {
        'X-API-Key': import.meta.env.VITE_API_KEY || 'taylordash-dev-key'
      };

      if (sessionToken) {
        headers['Authorization'] = `Bearer ${sessionToken}`;
      }

      const data = await measureAsyncPerformance(
        () => fetch(`/api/v1/logs?${params.toString()}`, { headers }).then(res => res.json()),
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
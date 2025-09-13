import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { getPluginById } from '../plugins/registry';
import { eventBusService } from '../services/eventBus';
import { ExternalLink, AlertTriangle, Loader } from 'lucide-react';

interface PluginPageProps {
  pluginId?: string;
}

export const PluginPage: React.FC<PluginPageProps> = ({ pluginId }) => {
  const params = useParams();
  const id = pluginId || params.pluginId;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const plugin = id ? getPluginById(id) : null;

  useEffect(() => {
    if (!plugin) {
      setError(`Plugin "${id}" not found`);
      setLoading(false);
      return;
    }

    // Simulate loading time for iframe
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, [plugin, id]);

  // Cleanup plugin registration on unmount
  useEffect(() => {
    if (!plugin || !id) return;

    // Cleanup on unmount
    return () => {
      eventBusService.unregisterPlugin(id);
      console.log(`[PluginPage] Unregistered plugin ${id} from event bus`);
    };
  }, [plugin, id]);

  if (!plugin) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Plugin Not Found</h1>
          <p className="text-gray-400">The plugin "{id}" could not be found.</p>
        </div>
      </div>
    );
  }

  // Determine the plugin URL based on environment
  const getPluginUrl = (plugin: any) => {
    const isDevelopment = import.meta.env.DEV;

    // Use the current window's hostname to work from remote machines
    const host = window.location.hostname;

    // Canonical port assignments - STANDARDIZED
    if (plugin.id === 'mcp-manager') {
      return isDevelopment ? `http://${host}:5174` : '/static/plugins/mcp-manager';
    } else if (plugin.id === 'midnight-hud') {
      return isDevelopment ? `http://${host}:5175` : '/static/plugins/midnight-hud';
    } else if (plugin.id === 'projects-manager') {
      return isDevelopment ? `http://${host}:5176` : '/static/plugins/projects-manager';
    }

    return '/404';
  };

  const pluginUrl = getPluginUrl(plugin);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-8 h-8 text-blue-400 mx-auto mb-4 animate-spin" />
          <h2 className="text-xl font-semibold mb-2">Loading {plugin.name}</h2>
          <p className="text-gray-400">Please wait while the plugin loads...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Plugin Error</h1>
          <p className="text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Plugin Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">{plugin.name}</h1>
            <span className="text-sm text-gray-400">v{plugin.version}</span>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              plugin.kind === 'ui' ? 'bg-blue-900 text-blue-300' :
              plugin.kind === 'data' ? 'bg-green-900 text-green-300' :
              'bg-purple-900 text-purple-300'
            }`}>
              {plugin.kind}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <a 
              href={pluginUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center px-3 py-1 text-sm text-gray-400 hover:text-white transition-colors"
            >
              <ExternalLink className="w-4 h-4 mr-1" />
              Open in new tab
            </a>
          </div>
        </div>
        {plugin.description && (
          <p className="text-gray-400 mt-2">{plugin.description}</p>
        )}
      </div>

      {/* Plugin Content */}
      <div className="relative" style={{ height: 'calc(100vh - 120px)' }}>
        <iframe
          ref={iframeRef}
          src={pluginUrl}
          className="w-full h-full border-0"
          title={plugin.name}
          sandbox="allow-scripts"
          style={{
            background: '#111827',
          }}
          onLoad={() => {
            console.log(`Plugin ${plugin.name} loaded successfully`);
            if (iframeRef.current && id) {
              eventBusService.registerPlugin(id, iframeRef.current);
              console.log(`[PluginPage] Registered plugin ${id} with event bus`);
            }
          }}
          onError={() => {
            setError(`Failed to load plugin: ${plugin.name}`);
          }}
        />
      </div>
    </div>
  );
};
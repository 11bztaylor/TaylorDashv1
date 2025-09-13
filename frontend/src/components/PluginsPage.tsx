import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { PLUGINS, Plugin } from '../plugins/registry';
import { ExternalLink, Play, Package, CheckCircle, Clock } from 'lucide-react';

export const PluginsPage: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'ui' | 'data' | 'integration'>('all');

  const filteredPlugins = filter === 'all'
    ? PLUGINS
    : PLUGINS.filter(plugin => plugin.kind === filter);

  const getStatusIcon = () => {
    // Since all plugins in registry are "installed", we'll show them as available
    return <CheckCircle className="w-5 h-5 text-green-400" />;
  };

  const getStatusText = () => {
    return 'Available';
  };

  const getStatusColor = () => {
    return 'text-green-400';
  };

  const getKindColor = (kind: Plugin['kind']) => {
    switch (kind) {
      case 'ui':
        return 'bg-blue-900 text-blue-300';
      case 'data':
        return 'bg-green-900 text-green-300';
      case 'integration':
        return 'bg-purple-900 text-purple-300';
      default:
        return 'bg-gray-900 text-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center">
                <Package className="w-8 h-8 mr-3 text-blue-400" />
                Plugin Store
              </h1>
              <p className="text-gray-400 mt-2">
                Discover and manage plugins for TaylorDash
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-400">{PLUGINS.length}</div>
              <div className="text-sm text-gray-400">Available Plugins</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Filter Tabs */}
        <div className="flex space-x-1 mb-8 bg-gray-800 p-1 rounded-lg w-fit">
          {[
            { key: 'all' as const, label: 'All Plugins', count: PLUGINS.length },
            { key: 'ui' as const, label: 'UI Plugins', count: PLUGINS.filter(p => p.kind === 'ui').length },
            { key: 'data' as const, label: 'Data Plugins', count: PLUGINS.filter(p => p.kind === 'data').length },
            { key: 'integration' as const, label: 'Integration', count: PLUGINS.filter(p => p.kind === 'integration').length },
          ].map(({ key, label, count }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === key
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              {label} ({count})
            </button>
          ))}
        </div>

        {/* Plugin Grid */}
        {filteredPlugins.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-400 mb-2">No plugins found</h3>
            <p className="text-gray-500">No plugins match the current filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPlugins.map((plugin) => (
              <div
                key={plugin.id}
                className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors"
              >
                {/* Plugin Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2">{plugin.name}</h3>
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getKindColor(plugin.kind)}`}>
                        {plugin.kind}
                      </span>
                      <span className="text-xs text-gray-400">v{plugin.version}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {getStatusIcon()}
                    <span className={`text-sm ${getStatusColor()}`}>
                      {getStatusText()}
                    </span>
                  </div>
                </div>

                {/* Plugin Description */}
                <p className="text-gray-400 text-sm mb-6 line-clamp-3">
                  {plugin.description || 'No description available.'}
                </p>

                {/* Plugin Actions */}
                <div className="flex space-x-3">
                  <Link
                    to={plugin.path}
                    className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Launch
                  </Link>
                  {plugin.entry_point && (
                    <a
                      href={plugin.entry_point}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
                      title="Open in new tab"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Plugin Development Info */}
        <div className="mt-12 bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
            <Clock className="w-5 h-5 mr-2 text-blue-400" />
            Plugin Development
          </h3>
          <p className="text-gray-400 mb-4">
            Want to create your own plugin? Check out the plugin development guide and examples.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="bg-gray-900 p-4 rounded-lg">
              <h4 className="font-medium text-white mb-2">UI Plugins</h4>
              <p className="text-gray-400">React-based interface plugins</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-lg">
              <h4 className="font-medium text-white mb-2">Data Plugins</h4>
              <p className="text-gray-400">Data processing and analysis tools</p>
            </div>
            <div className="bg-gray-900 p-4 rounded-lg">
              <h4 className="font-medium text-white mb-2">Integration Plugins</h4>
              <p className="text-gray-400">External service integrations</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
import React, { useState } from 'react';
import { 
  Search, 
  Plus, 
  Settings,
  Power,
  PowerOff,
  Download,
  Trash2,
  ExternalLink,
  Shield,
  Zap
} from 'lucide-react';
import { cn } from '@/utils';

export function PluginsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState<'installed' | 'available'>('installed');

  const installedPlugins = [
    {
      id: '1',
      name: 'System Monitor',
      version: '2.1.0',
      author: 'TaylorDash Team',
      description: 'Real-time system performance monitoring and alerts.',
      isEnabled: true,
      category: 'Monitoring',
      permissions: ['system_info', 'notifications'],
      lastUpdated: '2 days ago'
    },
    {
      id: '2',
      name: 'Git Integration',
      version: '1.5.3',
      author: 'DevTools Pro',
      description: 'Seamless Git repository management and status tracking.',
      isEnabled: true,
      category: 'Development',
      permissions: ['file_system'],
      lastUpdated: '1 week ago'
    },
    {
      id: '3',
      name: 'Docker Manager',
      version: '1.0.2',
      author: 'ContainerLabs',
      description: 'Monitor and manage Docker containers and images.',
      isEnabled: false,
      category: 'DevOps',
      permissions: ['system_info', 'network'],
      lastUpdated: '3 days ago'
    },
    {
      id: '4',
      name: 'Network Scanner',
      version: '0.9.1',
      author: 'SecurityTools',
      description: 'Scan and monitor network devices and services.',
      isEnabled: true,
      category: 'Security',
      permissions: ['network', 'system_info'],
      lastUpdated: '1 day ago'
    },
    {
      id: '5',
      name: 'Theme Editor',
      version: '1.2.4',
      author: 'DesignForge',
      description: 'Create and customize themes for TaylorDash.',
      isEnabled: false,
      category: 'Customization',
      permissions: ['file_system'],
      lastUpdated: '5 days ago'
    }
  ];

  const availablePlugins = [
    {
      id: '6',
      name: 'Cloud Storage',
      version: '2.0.0',
      author: 'CloudSync',
      description: 'Integrate with popular cloud storage providers.',
      downloads: 1234,
      rating: 4.8,
      category: 'Storage',
      price: 'Free'
    },
    {
      id: '7',
      name: 'API Monitor',
      version: '1.3.0',
      author: 'APITools',
      description: 'Monitor API endpoints and track response times.',
      downloads: 856,
      rating: 4.6,
      category: 'Monitoring',
      price: '$9.99'
    },
    {
      id: '8',
      name: 'Backup Manager',
      version: '1.1.0',
      author: 'BackupPro',
      description: 'Automated backup solutions for your data.',
      downloads: 432,
      rating: 4.5,
      category: 'Utility',
      price: 'Free'
    }
  ];

  const filteredInstalledPlugins = installedPlugins.filter(plugin =>
    plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    plugin.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredAvailablePlugins = availablePlugins.filter(plugin =>
    plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    plugin.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const togglePlugin = (pluginId: string) => {
    // In a real app, this would call an API to enable/disable the plugin
    console.log('Toggle plugin:', pluginId);
  };

  const uninstallPlugin = (pluginId: string) => {
    // In a real app, this would call an API to uninstall the plugin
    console.log('Uninstall plugin:', pluginId);
  };

  const installPlugin = (pluginId: string) => {
    // In a real app, this would call an API to install the plugin
    console.log('Install plugin:', pluginId);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="h-16 border-b border-midnight-700/50 px-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-midnight-100">Plugins</h1>
          <p className="text-sm text-midnight-400">
            Extend TaylorDash with powerful plugins
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-midnight-400" />
            <input
              type="text"
              placeholder="Search plugins..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-cyber pl-10 w-64"
            />
          </div>

          <button className="btn-cyber">
            <Plus className="w-4 h-4 mr-2" />
            Install Plugin
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-midnight-700/50">
        <div className="px-6">
          <div className="flex space-x-8">
            {[
              { id: 'installed', label: 'Installed', count: installedPlugins.length },
              { id: 'available', label: 'Available', count: availablePlugins.length }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id as any)}
                className={cn(
                  'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                  selectedTab === tab.id
                    ? 'border-cyber-500 text-cyber-300'
                    : 'border-transparent text-midnight-400 hover:text-midnight-300'
                )}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto scrollbar-cyber p-6">
        {selectedTab === 'installed' ? (
          <div className="space-y-4">
            {filteredInstalledPlugins.map((plugin) => (
              <div key={plugin.id} className="panel-midnight p-6 rounded-xl">
                <div className="flex items-start justify-between">
                  {/* Plugin Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className={cn(
                        'w-10 h-10 rounded-lg flex items-center justify-center',
                        plugin.isEnabled ? 'bg-cyber-500/20' : 'bg-midnight-700/50'
                      )}>
                        <Zap className={cn(
                          'w-5 h-5',
                          plugin.isEnabled ? 'text-cyber-400' : 'text-midnight-400'
                        )} />
                      </div>
                      
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-midnight-100">
                            {plugin.name}
                          </h3>
                          <span className="text-xs text-midnight-400">
                            v{plugin.version}
                          </span>
                          <span className={cn(
                            'px-2 py-0.5 rounded-full text-xs',
                            plugin.isEnabled 
                              ? 'bg-cyber-500/20 text-cyber-300'
                              : 'bg-midnight-700 text-midnight-400'
                          )}>
                            {plugin.isEnabled ? 'Enabled' : 'Disabled'}
                          </span>
                        </div>
                        <p className="text-sm text-midnight-400">
                          by {plugin.author} • {plugin.category}
                        </p>
                      </div>
                    </div>

                    <p className="text-sm text-midnight-300 mb-3">
                      {plugin.description}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-midnight-400">
                      <span>Updated {plugin.lastUpdated}</span>
                      <div className="flex items-center gap-1">
                        <Shield className="w-3 h-3" />
                        <span>{plugin.permissions.length} permissions</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => togglePlugin(plugin.id)}
                      className={cn(
                        'p-2 rounded-lg transition-colors',
                        plugin.isEnabled
                          ? 'text-cyber-400 hover:bg-cyber-500/20'
                          : 'text-midnight-400 hover:bg-midnight-700/50'
                      )}
                      title={plugin.isEnabled ? 'Disable' : 'Enable'}
                    >
                      {plugin.isEnabled ? (
                        <Power className="w-4 h-4" />
                      ) : (
                        <PowerOff className="w-4 h-4" />
                      )}
                    </button>

                    <button
                      className="p-2 rounded-lg text-midnight-400 hover:text-midnight-300 hover:bg-midnight-700/50 transition-colors"
                      title="Settings"
                    >
                      <Settings className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => uninstallPlugin(plugin.id)}
                      className="p-2 rounded-lg text-midnight-400 hover:text-red-400 hover:bg-red-500/20 transition-colors"
                      title="Uninstall"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAvailablePlugins.map((plugin) => (
              <div key={plugin.id} className="panel-midnight p-6 rounded-xl hover:border-cyber-500/50 transition-all duration-300 group">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-cyber rounded-lg flex items-center justify-center">
                    <Zap className="w-6 h-6 text-midnight-900" />
                  </div>
                  
                  <div className="text-right">
                    <div className={cn(
                      'text-sm font-semibold',
                      plugin.price === 'Free' ? 'text-cyber-400' : 'text-orange-400'
                    )}>
                      {plugin.price}
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-midnight-100 group-hover:text-cyber-300 transition-colors">
                      {plugin.name}
                    </h3>
                    <span className="text-xs text-midnight-400">
                      v{plugin.version}
                    </span>
                  </div>
                  <p className="text-xs text-midnight-400 mb-2">
                    by {plugin.author} • {plugin.category}
                  </p>
                  <p className="text-sm text-midnight-300 line-clamp-2">
                    {plugin.description}
                  </p>
                </div>

                {/* Stats */}
                <div className="flex items-center justify-between text-xs text-midnight-400 mb-4">
                  <div className="flex items-center gap-2">
                    <span>★ {plugin.rating}</span>
                    <span>•</span>
                    <span>{plugin.downloads} downloads</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => installPlugin(plugin.id)}
                    className="btn-cyber flex-1 text-sm"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Install
                  </button>
                  <button className="btn-cyber-outline px-3 py-2 text-sm">
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
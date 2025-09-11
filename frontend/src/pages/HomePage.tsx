import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Play, 
  Plus, 
  Layout, 
  Zap, 
  Settings,
  ArrowRight
} from 'lucide-react';
import { cn } from '@/utils';

export function HomePage() {
  const recentCanvases = [
    { id: '1', name: 'Development Dashboard', lastModified: '2 hours ago' },
    { id: '2', name: 'System Monitor', lastModified: '1 day ago' },
    { id: '3', name: 'Project Overview', lastModified: '3 days ago' },
  ];

  const quickActions = [
    {
      id: 'new-canvas',
      title: 'New Canvas',
      description: 'Create a fresh workspace',
      icon: Plus,
      action: '/canvas/new',
      color: 'cyber'
    },
    {
      id: 'templates',
      title: 'Templates',
      description: 'Start from a template',
      icon: Layout,
      action: '/library',
      color: 'orange'
    },
    {
      id: 'plugins',
      title: 'Browse Plugins',
      description: 'Extend functionality',
      icon: Zap,
      action: '/plugins',
      color: 'purple'
    },
    {
      id: 'settings',
      title: 'Settings',
      description: 'Configure preferences',
      icon: Settings,
      action: '/settings',
      color: 'blue'
    },
  ];

  return (
    <div className="h-full overflow-auto scrollbar-cyber">
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl lg:text-5xl font-bold text-cyber-gradient">
            Welcome to TaylorDash
          </h1>
          <p className="text-lg text-midnight-300 max-w-2xl mx-auto">
            Your visual shell interface for managing projects, monitoring systems, and orchestrating workflows.
          </p>
        </div>

        {/* Quick Actions Grid */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-midnight-100 flex items-center gap-2">
            <Zap className="w-6 h-6 text-cyber-400" />
            Quick Actions
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Link
                  key={action.id}
                  to={action.action}
                  className={cn(
                    'group relative p-6 rounded-xl border transition-all duration-300',
                    'hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-midnight-900',
                    'panel-midnight hover:border-cyber-500/50'
                  )}
                >
                  <div className="space-y-3">
                    <div className={cn(
                      'w-12 h-12 rounded-lg flex items-center justify-center',
                      action.color === 'cyber' && 'bg-cyber-500/20 text-cyber-400',
                      action.color === 'orange' && 'bg-orange-500/20 text-orange-400',
                      action.color === 'purple' && 'bg-purple-500/20 text-purple-400',
                      action.color === 'blue' && 'bg-blue-500/20 text-blue-400'
                    )}>
                      <Icon className="w-6 h-6" />
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-midnight-100 group-hover:text-cyber-300 transition-colors">
                        {action.title}
                      </h3>
                      <p className="text-sm text-midnight-400">
                        {action.description}
                      </p>
                    </div>
                    
                    <ArrowRight className="w-4 h-4 text-midnight-500 group-hover:text-cyber-400 group-hover:translate-x-1 transition-all ml-auto" />
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* Recent Canvases */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-midnight-100 flex items-center gap-2">
              <Layout className="w-6 h-6 text-cyber-400" />
              Recent Canvases
            </h2>
            <Link 
              to="/canvas" 
              className="text-cyber-400 hover:text-cyber-300 transition-colors text-sm font-medium flex items-center gap-1"
            >
              View all
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentCanvases.map((canvas) => (
              <Link
                key={canvas.id}
                to={`/canvas/${canvas.id}`}
                className="group panel-midnight p-4 rounded-xl hover:border-cyber-500/50 transition-all duration-300 hover:scale-102"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 bg-gradient-cyber rounded-lg flex items-center justify-center">
                    <Layout className="w-5 h-5 text-midnight-900" />
                  </div>
                  <Play className="w-4 h-4 text-midnight-500 group-hover:text-cyber-400 transition-colors" />
                </div>
                
                <h3 className="font-semibold text-midnight-100 group-hover:text-cyber-300 transition-colors mb-1">
                  {canvas.name}
                </h3>
                <p className="text-sm text-midnight-400">
                  Modified {canvas.lastModified}
                </p>
              </Link>
            ))}
          </div>
        </section>

        {/* System Status */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-midnight-100">
            System Status
          </h2>
          
          <div className="panel-midnight p-6 rounded-xl">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-cyber-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <div className="w-8 h-8 bg-cyber-400 rounded-full animate-pulse-cyber"></div>
                </div>
                <h3 className="font-semibold text-midnight-100">System Online</h3>
                <p className="text-sm text-midnight-400">All services running</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Zap className="w-8 h-8 text-orange-400" />
                </div>
                <h3 className="font-semibold text-midnight-100">5 Plugins Active</h3>
                <p className="text-sm text-midnight-400">Ready to use</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Layout className="w-8 h-8 text-purple-400" />
                </div>
                <h3 className="font-semibold text-midnight-100">3 Canvases</h3>
                <p className="text-sm text-midnight-400">In workspace</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
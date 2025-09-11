import React, { useState, useEffect } from 'react';
import { Project, projectsApi } from '../services/api';
import { pluginEventService, ProjectEvent } from '../services/eventService';
import { Folder, Calendar, User, MoreVertical, Wifi, WifiOff } from 'lucide-react';

interface ProjectsListProps {
  onProjectsChange?: () => void;
}

export const ProjectsList: React.FC<ProjectsListProps> = ({ onProjectsChange }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const [lastEventTime, setLastEventTime] = useState<string>('');

  const fetchProjects = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await projectsApi.getAll();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      setError('Failed to load projects. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (onProjectsChange) {
      fetchProjects();
    }
  }, [onProjectsChange]);

  // Set up real-time event subscriptions
  useEffect(() => {
    const unsubscribe = pluginEventService.subscribeToProjectEvents((event: ProjectEvent) => {
      console.log('[ProjectsList] Received project event:', event);
      setLastEventTime(new Date().toLocaleTimeString());
      
      // Update projects based on event type
      switch (event.type) {
        case 'project_created':
          // Refresh the entire list to get the new project
          fetchProjects();
          break;
          
        case 'project_updated':
          setProjects(prevProjects => 
            prevProjects.map(project => 
              project.id === event.data.project_id
                ? { ...project, ...event.data, updated_at: event.timestamp }
                : project
            )
          );
          break;
          
        case 'project_deleted':
          setProjects(prevProjects => 
            prevProjects.filter(project => project.id !== event.data.project_id)
          );
          break;
      }
    });

    // Subscribe to system events for connection status
    const unsubscribeSystem = pluginEventService.subscribeToSystemEvents((event) => {
      if (event.type === 'connection_status') {
        const connected = event.data.status === 'connected';
        setIsConnected(connected);
      }
    });

    // Check initial connection status
    const connectionStatus = pluginEventService.getConnectionStatus();
    setIsConnected(connectionStatus === 'ready');

    return () => {
      unsubscribe();
      unsubscribeSystem();
    };
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-900 text-green-300';
      case 'completed': return 'bg-blue-900 text-blue-300';
      case 'on_hold': return 'bg-yellow-900 text-yellow-300';
      default: return 'bg-gray-600 text-gray-300';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Invalid date';
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <Folder className="w-5 h-5 mr-2" />
          Projects
        </h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-400">Loading projects...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <Folder className="w-5 h-5 mr-2" />
          Projects
        </h2>
        <div className="bg-red-900 border border-red-700 rounded-lg p-4">
          <p className="text-red-300">{error}</p>
          <button 
            onClick={fetchProjects}
            className="mt-3 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-lg text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          <Folder className="w-5 h-5 mr-2" />
          Projects ({projects.length})
        </h2>
        <div className="flex items-center space-x-3">
          {lastEventTime && (
            <span className="text-xs text-gray-500">
              Last update: {lastEventTime}
            </span>
          )}
          <div className="flex items-center space-x-1">
            {isConnected ? (
              <Wifi className="w-4 h-4 text-green-400" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-400" />
            )}
            <span className="text-xs text-gray-400">
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
      </div>
      
      {projects.length === 0 ? (
        <div className="text-center py-8">
          <Folder className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400 text-sm">
            No projects yet. Start by creating your first project!
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <div key={project.id} className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-white font-medium flex items-center">
                    <Folder className="w-4 h-4 mr-2 text-blue-400" />
                    {project.name}
                  </h3>
                  {project.description && (
                    <p className="text-gray-300 text-sm mt-1">{project.description}</p>
                  )}
                  
                  <div className="flex items-center mt-3 space-x-4 text-xs text-gray-400">
                    <div className="flex items-center">
                      <Calendar className="w-3 h-3 mr-1" />
                      {formatDate(project.created_at)}
                    </div>
                    {project.owner_id && (
                      <div className="flex items-center">
                        <User className="w-3 h-3 mr-1" />
                        {project.owner_id.slice(0, 8)}...
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(project.status)}`}>
                    {project.status.replace('_', ' ')}
                  </span>
                  <button className="p-1 text-gray-400 hover:text-white transition-colors">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
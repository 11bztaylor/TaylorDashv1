import React, { useState, useEffect } from 'react';
import { RefreshCw, Plus, Folder, Clock, CheckCircle, XCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { Project } from '../types/api';

export const ProjectsList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError('');
      const projectsData = await apiService.getProjects();
      setProjects(projectsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
      console.error('Error loading projects:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const getStatusIcon = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'inactive':
        return <XCircle className="w-4 h-4 text-gray-500" />;
      default:
        return <Folder className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'completed':
        return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'inactive':
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center">
            <Folder className="w-5 h-5 mr-2" />
            Projects
          </h2>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-400">Loading projects...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          <Folder className="w-5 h-5 mr-2" />
          Projects
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={loadProjects}
            className="flex items-center px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </button>
          <button className="flex items-center px-3 py-1 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors">
            <Plus className="w-4 h-4 mr-1" />
            New Project
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500/30 text-red-300 px-4 py-3 rounded mb-4">
          <p className="text-sm">Error loading projects: {error}</p>
          <button
            onClick={loadProjects}
            className="text-xs underline hover:no-underline mt-1"
          >
            Try again
          </button>
        </div>
      )}

      {projects.length === 0 && !error ? (
        <div className="text-center py-8 text-gray-400">
          <Folder className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-lg mb-2">No projects found</p>
          <p className="text-sm">Create your first project to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <div
              key={project.id}
              className="flex items-center justify-between p-4 bg-gray-700 rounded-lg hover:bg-gray-650 transition-colors"
            >
              <div className="flex items-center space-x-3">
                {getStatusIcon(project.status)}
                <div>
                  <h3 className="text-white font-medium">{project.name}</h3>
                  {project.description && (
                    <p className="text-sm text-gray-400 mt-1">{project.description}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    Updated: {new Date(project.updated_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span
                  className={`px-2 py-1 text-xs rounded border ${getStatusColor(project.status)}`}
                >
                  {project.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
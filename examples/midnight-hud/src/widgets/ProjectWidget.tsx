import React from 'react';
import { FolderOpen, Play, Pause, AlertCircle } from 'lucide-react';
import type { ProjectData } from '../types/dashboard';

interface ProjectWidgetProps {
  data: ProjectData[];
  isMinimized: boolean;
}

export const ProjectWidget: React.FC<ProjectWidgetProps> = ({ data, isMinimized }) => {
  if (isMinimized) {
    const runningCount = data.filter(p => p.status === 'running').length;
    return (
      <div className="flex items-center space-x-2 p-2">
        <FolderOpen className="w-4 h-4 text-blue-400" />
        <span className="text-sm text-white">{runningCount} running</span>
      </div>
    );
  }

  const getStatusIcon = (status: ProjectData['status']) => {
    switch (status) {
      case 'running':
        return <Play className="w-3 h-3 text-green-400" />;
      case 'idle':
        return <Pause className="w-3 h-3 text-yellow-400" />;
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-400" />;
    }
  };

  const getStatusColor = (status: ProjectData['status']) => {
    switch (status) {
      case 'running':
        return 'text-green-400';
      case 'idle':
        return 'text-yellow-400';
      case 'error':
        return 'text-red-400';
    }
  };

  return (
    <div className="p-4 space-y-3">
      <div className="space-y-2">
        {data.map((project, index) => (
          <div key={index} className="border border-gray-700/50 rounded-lg p-3 bg-black/20">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">{project.name}</span>
              <div className="flex items-center space-x-1">
                {getStatusIcon(project.status)}
                <span className={`text-xs ${getStatusColor(project.status)}`}>
                  {project.status}
                </span>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Progress</span>
                <span className="text-white">{project.progress}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-1">
                <div 
                  className="bg-cyan-400 h-1 rounded-full" 
                  style={{ width: `${project.progress}%` }}
                />
              </div>
              <div className="text-xs text-gray-400">
                Last update: {project.lastUpdate}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
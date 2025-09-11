import React, { useState } from 'react';
import { ProjectsList } from '../components/ProjectsList';
import { ProjectCreateModal } from '../components/ProjectCreateModal';
import { Plus, FolderOpen } from 'lucide-react';

export const ProjectsPage: React.FC = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [projectsRefreshTrigger, setProjectsRefreshTrigger] = useState(0);

  const handleProjectCreated = () => {
    setProjectsRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center">
              <FolderOpen className="w-8 h-8 mr-3 text-blue-400" />
              Project Manager
            </h1>
            <p className="text-gray-400 mt-2">
              Manage your projects and track progress from this centralized dashboard
            </p>
          </div>
          
          <button 
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </button>
        </div>
      </div>

      {/* Projects List */}
      <ProjectsList 
        key={projectsRefreshTrigger}
        onProjectsChange={projectsRefreshTrigger > 0 ? () => {} : undefined}
      />

      {/* Create Modal */}
      <ProjectCreateModal 
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleProjectCreated}
      />

      {/* Plugin Info Footer */}
      <div className="mt-8 p-4 bg-gray-800 rounded-lg border border-gray-700">
        <div className="flex items-center text-sm text-gray-400">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
            <span>Projects Manager Plugin v0.1.0</span>
          </div>
          <span className="mx-4">•</span>
          <span>Connected to TaylorDash API</span>
          <span className="mx-4">•</span>
          <span>Running on port 5175</span>
        </div>
      </div>
    </div>
  );
};
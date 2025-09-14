import React, { useState } from 'react';
import { Layout } from './Layout';
import { ProjectsList } from './ProjectsList';
import { ProjectCreateModal } from './ProjectCreateModal';

export const ProjectsView: React.FC = () => {
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
import React from 'react';
import { Layout } from './Layout';
import { ProjectsList } from './ProjectsList';
import { FlowCanvas } from './FlowCanvas';

export const Dashboard: React.FC = () => {
  return (
    <Layout title="Dashboard">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-16">
        {/* Projects Section */}
        <div className="space-y-6">
          <ProjectsList />
        </div>

        {/* Canvas Section */}
        <div className="space-y-6">
          <FlowCanvas />
        </div>
      </div>
    </Layout>
  );
};
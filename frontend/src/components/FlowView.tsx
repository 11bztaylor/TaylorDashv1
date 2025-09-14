import React from 'react';
import { Layout } from './Layout';
import { FlowCanvas } from './FlowCanvas';

export const FlowView: React.FC = () => {
  return (
    <Layout title="Flow Canvas">
      <div className="pb-16 h-screen">
        <FlowCanvas />
      </div>
    </Layout>
  );
};
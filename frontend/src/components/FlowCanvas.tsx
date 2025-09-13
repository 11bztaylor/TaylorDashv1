import React, { useCallback } from 'react';
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
} from '@reactflow/core';
import { Controls } from '@reactflow/controls';
import { Background } from '@reactflow/background';
import { MiniMap } from '@reactflow/minimap';
import '@reactflow/core/dist/style.css';

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'default',
    position: { x: 250, y: 50 },
    data: { label: 'TaylorDash Backend' },
    style: { background: '#1f2937', color: '#ffffff', border: '1px solid #374151' },
  },
  {
    id: '2',
    type: 'default',
    position: { x: 100, y: 200 },
    data: { label: 'Projects API' },
    style: { background: '#065f46', color: '#ffffff', border: '1px solid #059669' },
  },
  {
    id: '3',
    type: 'default',
    position: { x: 400, y: 200 },
    data: { label: 'Frontend Dashboard' },
    style: { background: '#1e3a8a', color: '#ffffff', border: '1px solid #3b82f6' },
  },
];

const initialEdges: Edge[] = [
  {
    id: 'e1-2',
    source: '1',
    target: '2',
    type: 'smoothstep',
    style: { stroke: '#059669' },
  },
  {
    id: 'e1-3',
    source: '1',
    target: '3',
    type: 'smoothstep',
    style: { stroke: '#3b82f6' },
  },
];

export const FlowCanvas: React.FC = () => {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">System Architecture</h2>
        <div className="flex space-x-2">
          <button className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-colors">
            Reset View
          </button>
          <button className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors">
            Add Node
          </button>
        </div>
      </div>
      
      <div className="h-96 bg-gray-900 rounded-lg overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          style={{ background: '#111827' }}
        >
          <Controls className="bg-gray-800 border-gray-600" />
          <Background color="#374151" gap={20} />
          <MiniMap 
            nodeColor="#374151"
            maskColor="rgba(17, 24, 39, 0.8)"
            className="bg-gray-800 border-gray-600"
          />
        </ReactFlow>
      </div>
      
      <div className="mt-4 text-sm text-gray-400">
        <p>Interactive system diagram - drag nodes to rearrange, click and drag from connection points to create new relationships.</p>
      </div>
    </div>
  );
};